import * as THREE from 'three';
import {GLTFLoader} from 'three/addons/loaders/GLTFLoader.js';
import {MeshoptDecoder} from 'three/addons/libs/meshopt_decoder.module.js';
import { OrbitControls } from 'three/addons/controls/OrbitControls.js';


function logTime(label) {
    console.log(`⏱ ${label}: ${(performance.now() / 1000).toFixed(2)} s since page start`);
}

const scene = new THREE.Scene();
scene.background = new THREE.Color(0xEDE8D0);

const camera = new THREE.PerspectiveCamera(75, window.innerWidth / window.innerHeight, 0.1, 1000);
const loader = new GLTFLoader();
loader.setMeshoptDecoder(MeshoptDecoder);

const AmbientLight = new THREE.AmbientLight( 0xffffff, 0.75 );
const DirectionalLight = new THREE.DirectionalLight(0xffffff, 0.75)
scene.add( AmbientLight, DirectionalLight );

const renderer = new THREE.WebGLRenderer();
renderer.setSize(window.innerWidth, window.innerHeight);
const rDom = renderer.domElement;
document.body.appendChild(rDom);

const controls = new OrbitControls( camera, rDom );

renderer.setAnimationLoop(() => {
    controls.update();
    renderer.render( scene, camera );
});

controls.enableDamping = true;
controls.dampingFactor = 0.08;

let model;
loader.load(
    '/assets/blazer.glb',

    function(gltf) {
    model = gltf.scene;
    const box = new THREE.Box3().setFromObject(gltf.scene);
    const size = box.getSize(new THREE.Vector3());
    const center = box.getCenter(new THREE.Vector3());
    console.log(size, center);

    controls.target.copy(center);
    controls.minDistance = 0.5 * size.y;
    controls.maxDistance = 4 * size.y;
    controls.update();
    camera.position.copy(center);
    camera.position.z += 2.5 * size.y;
    controls.saveState();
    
    camera.near = 0.01 * size.y;
    camera.far = 10 * size.y;
    camera.updateProjectionMatrix();

    model.traverse(o => console.log(o.type, o.name));
    model.getObjectByName('left_pocket').children.forEach(c => console.log(c.name, c.material.name));
    model.getObjectByName('right_pocket').children.forEach(c => console.log(c.name, c.material.name));

    scene.add(model);
    requestAnimationFrame(() => logTime('Jacket on screen'));
    apply();
    },
    
    function(xhr) {
    if (xhr.total > 0) {
        const percentageCompleted = (xhr.loaded / xhr.total) * 100;
        console.log( `Model is ${ Math.round( percentageCompleted ) }% loaded` );
    } else {
        console.log( `Downloaded ${ ( xhr.loaded / 1024 / 1024 ).toFixed( 2 ) } MB` );
    }
    },

    function ( error ) {
    console.error( 'Error:', error );
}

)

const state = {buttons: 2, cuffs: true, flapPockets: 2, patchPocket: true, lining: '#228B22', fabric: 'wool'};

const LOOKUP = {
    buttons: { 0: [], 2: ['closure2_button'], 3: ['closure2_button', 'closure3_button'] },
    cuffs: {false: [], true: ['cuff_buttons']},
    flapPockets: { 0: [], 1: ['left_pocket'], 2: ['right_pocket'], 3: ['left_pocket', 'right_pocket'] },
    patchPocket: {false: [], true: ['chest_pocket']}
};

const TOGGLEABLE = new Set(Object.values(LOOKUP).flatMap(g => Object.values(g).flat()));

const CLOTH_PARTS = ['body', 'collar', 'left_sleeve', 'right_sleeve', 'left_pocket', 'right_pocket', 'chest_pocket'];

function apply() {
    if (!model) return;
    const on = new Set([...LOOKUP.buttons[state.buttons], ...LOOKUP.cuffs[state.cuffs], ...LOOKUP.flapPockets[state.flapPockets], ...LOOKUP.patchPocket[state.patchPocket]]);

    for (const name of TOGGLEABLE) model.getObjectByName(name).visible = on.has(name);

    for (const part of CLOTH_PARTS) setFabric(model.getObjectByName(part), {fabric: state.fabric});
    setFabric(model.getObjectByName('lining'), {color: state.lining});
}

const FABRICS = [
    { id: 'wool',   swatch: '/assets/Fabrics/Fabric031_2K-JPG_Color.jpg' },
    { id: 'stripe', swatch: '/assets/Fabrics/Fabric072_2K-JPG_Color.jpg' },
    { id: 'check',  swatch: '/assets/Fabrics/Fabric083_2K-JPG_Color.jpg' },
];

let fabricLogged = false;
async function setFabric(mesh, {color=0xffffff, fabric=null} = {}) {
    const mat = clothMesh(mesh).material;
    mat.color.set(color);

    const url = FABRICS.find(f => f.id === fabric)?.swatch;
    mat.map = url ? await getTexture(url) : null;
    mat.needsUpdate = true;

    mat.needsUpdate = true;
    if (!fabricLogged) {
        fabricLogged = true;
        logTime('First fabric texture applied');
    }
}

function clothMesh(obj) {
    if (obj.isMesh) return obj;
    return obj.children.find(c => c.material.name === 'kruvaze_blazer_FRONT_2303');
}

const texLoader = new THREE.TextureLoader();
const texCache = new Map();

async function getTexture(url) {
    if (!texCache.has(url)) {
    const tex = await texLoader.loadAsync(url);
    tex.flipY = false;
    tex.wrapS = tex.wrapT = THREE.RepeatWrapping;
    tex.colorSpace = THREE.SRGBColorSpace;
    tex.anisotropy = renderer.capabilities.getMaxAnisotropy();
    texCache.set(url, tex);
    }
    return texCache.get(url);
}

const optionButtons = document.querySelectorAll('button[data-option]');

function toValue(text) {
    if (text === 'true') return true;
    if (text === 'false') return false;
    if (text !== '' && !isNaN(text)) return Number(text);
    return text;
}

function refreshButtons() {
    for (const b of optionButtons) {
        b.classList.toggle('active', state[b.dataset.option] === toValue(b.dataset.value));
    }
}

for (const b of optionButtons) {
    b.addEventListener('click', () => {
        state[b.dataset.option] = toValue(b.dataset.value);
        refreshButtons();
        apply();
    });
}

document.getElementById('reset').addEventListener('click', () => {
  controls.enableDamping = false;
  controls.update();
  controls.reset();
  controls.enableDamping = true;
});

const liningPicker = document.getElementById('liningPicker');
liningPicker.value = state.lining;
liningPicker.addEventListener('input', () => {
    state.lining = liningPicker.value;
    apply();
});

refreshButtons();

window.addEventListener('resize', () => {
    camera.aspect = window.innerWidth / window.innerHeight;
    camera.updateProjectionMatrix();
    renderer.setSize(window.innerWidth, window.innerHeight);
});