import * as THREE from 'three';

// The CLO buttons are merged into a few meshes (closure2_button, closure3_button, cuff_buttons),
// and every button is about 12 small pieces (body, rim, thread loops).
// findButtons() works out where each button sits, how big it is and which way it faces,
// so a new button model can be placed on the same spot.

// All vertices of a mesh in world space, plus its triangles as [i, j, k] vertex ids.
function readMesh(mesh) {
    mesh.updateWorldMatrix(true, false);
    const pos = mesh.geometry.attributes.position;
    const index = mesh.geometry.index;
    const points = [];
    for (let i = 0; i < pos.count; i++) {
        points.push(new THREE.Vector3().fromBufferAttribute(pos, i).applyMatrix4(mesh.matrixWorld));
    }
    const count = index ? index.count : pos.count;
    const tris = [];
    for (let i = 0; i < count; i += 3) {
        const at = k => (index ? index.getX(i + k) : i + k);
        tris.push([at(0), at(1), at(2)]);
    }
    return { points, tris };
}

// Groups triangles that touch each other. The glTF exporter duplicates vertices along
// normal/UV seams, so vertices at the same position are welded first.
function connectedPieces({ points, tris }) {
    const weld = new Map();
    const id = points.map(p => {
        const key = `${Math.round(p.x * 1000)},${Math.round(p.y * 1000)},${Math.round(p.z * 1000)}`;
        if (!weld.has(key)) weld.set(key, weld.size);
        return weld.get(key);
    });

    const parent = [...Array(weld.size).keys()];
    const find = a => (parent[a] === a ? a : (parent[a] = find(parent[a])));
    for (const [a, b, c] of tris) {
        parent[find(id[b])] = find(id[a]);
        parent[find(id[c])] = find(id[a]);
    }

    const pieces = new Map();
    tris.forEach(([a, b, c]) => {
        const root = find(id[a]);
        if (!pieces.has(root)) pieces.set(root, { faces: 0, ids: new Set(), points: [] });
        const piece = pieces.get(root);
        piece.faces++;
        for (const v of [a, b, c]) {
            if (!piece.ids.has(id[v])) {
                piece.ids.add(id[v]);
                piece.points.push(points[v]);
            }
        }
    });
    return [...pieces.values()];
}

// The two biggest directions of spread of a point cloud. Their cross product is the normal
// of a flat disc, which is what a button is.
function discNormal(points, centre) {
    let xx = 0, xy = 0, xz = 0, yy = 0, yz = 0, zz = 0;
    for (const p of points) {
        const x = p.x - centre.x, y = p.y - centre.y, z = p.z - centre.z;
        xx += x * x; xy += x * y; xz += x * z; yy += y * y; yz += y * z; zz += z * z;
    }
    const C = [[xx, xy, xz], [xy, yy, yz], [xz, yz, zz]];
    const mul = (m, v) => new THREE.Vector3(
        m[0][0] * v.x + m[0][1] * v.y + m[0][2] * v.z,
        m[1][0] * v.x + m[1][1] * v.y + m[1][2] * v.z,
        m[2][0] * v.x + m[2][1] * v.y + m[2][2] * v.z);

    let a = new THREE.Vector3(1, 0.3, 0.2).normalize();
    for (let i = 0; i < 60; i++) a = mul(C, a).normalize();

    const lambda = mul(C, a).dot(a);
    const av = [a.x, a.y, a.z];
    const D = C.map((row, i) => row.map((c, j) => c - lambda * av[i] * av[j]));
    let b = new THREE.Vector3(0.1, 1, 0.3);
    b.addScaledVector(a, -b.dot(a)).normalize();
    for (let i = 0; i < 60; i++) b = mul(D, b).normalize();

    return { n: new THREE.Vector3().crossVectors(a, b).normalize(), a, b };
}

// Middle of a sleeve tube at a given height: the average of its vertices within 1.5 cm of that height.
function sleeveAxisAt(sleeve, y) {
    sleeve.updateWorldMatrix(true, false);
    const pos = sleeve.geometry.attributes.position;
    const sum = new THREE.Vector3(), p = new THREE.Vector3();
    let count = 0;
    for (let i = 0; i < pos.count; i++) {
        p.fromBufferAttribute(pos, i).applyMatrix4(sleeve.matrixWorld);
        if (Math.abs(p.y - y) < 1.5) { sum.add(p); count++; }
    }
    return count ? sum.divideScalar(count) : null;
}

// mesh:    the merged CLO mesh that holds the button pieces (e.g. the 'Material500086' child)
// facing:  a THREE.Vector3 the buttons should face (the front of the jacket is +Z), or the sleeve mesh(es)
//          for cuff buttons (a mesh or an array of meshes): the button then faces away from the
//          centre line of the nearest sleeve at that height.
// Returns one { origin, normal, diameter, thickness } per button, all in world space.
// origin is the centre of the button's BACK face, which is where your button models have y = 0.
export function findButtons(mesh, facing) {
    const pieces = connectedPieces(readMesh(mesh));
    const biggest = Math.max(...pieces.map(p => p.faces));
    const bodies = pieces.filter(p => p.faces >= 0.5 * biggest);       // one body per button

    return bodies.map(body => {
        const centre = body.points.reduce((s, p) => s.add(p), new THREE.Vector3()).divideScalar(body.points.length);
        const { n, a, b } = discNormal(body.points, centre);

        let outward = facing;
        if (!facing.isVector3) {
            // sleeve(s): face away from the centre line of the nearest sleeve at this height
            const axes = [].concat(facing).map(s => sleeveAxisAt(s, centre.y)).filter(Boolean);
            const axis = axes.sort((p, q) => p.distanceTo(centre) - q.distanceTo(centre))[0];
            outward = centre.clone().sub(axis);
            outward.y = 0;
        }
        if (n.dot(outward) < 0) n.negate();

        let lo = Infinity, hi = -Infinity, widthA = [Infinity, -Infinity], widthB = [Infinity, -Infinity];
        for (const p of body.points) {
            const d = p.clone().sub(centre);
            lo = Math.min(lo, d.dot(n)); hi = Math.max(hi, d.dot(n));
            widthA = [Math.min(widthA[0], d.dot(a)), Math.max(widthA[1], d.dot(a))];
            widthB = [Math.min(widthB[0], d.dot(b)), Math.max(widthB[1], d.dot(b))];
        }
        return {
            origin: centre.clone().addScaledVector(n, lo),
            normal: n,
            diameter: Math.max(widthA[1] - widthA[0], widthB[1] - widthB[0]),
            thickness: hi - lo,
        };
    });
}

// Puts a copy of a button model on a spot found by findButtons().
// The models are 2.2 cm wide with the back at y = 0 and the face pointing along +Y.
export function placeButton(template, spot, modelDiameter = 2.2) {
    const copy = template.clone();
    copy.scale.setScalar(spot.diameter / modelDiameter);
    copy.quaternion.setFromUnitVectors(new THREE.Vector3(0, 1, 0), spot.normal);
    copy.position.copy(spot.origin);
    return copy;
}