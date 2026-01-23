console.log("three-bg.js LOADED");


const canvas = document.getElementById("bg");

const scene = new THREE.Scene();
scene.background = new THREE.Color(0x020617);

const camera = new THREE.PerspectiveCamera(
    75,
    window.innerWidth / window.innerHeight,
    0.1,
    1000
);

const renderer = new THREE.WebGLRenderer({
    canvas,
    alpha: true,
    antialias: true
});

renderer.setSize(window.innerWidth, window.innerHeight, false);
renderer.setPixelRatio(window.devicePixelRatio);
renderer.domElement.style.pointerEvents = "none";

camera.position.z = 5;

const ambientLight = new THREE.AmbientLight(0xffffff, 0.6);
scene.add(ambientLight);

const pointLight = new THREE.PointLight(0x22c55e, 1.5);
pointLight.position.set(5, 5, 5);
scene.add(pointLight);


const sphereGeometry = new THREE.SphereGeometry(1.2, 64, 64);
const sphereMaterial = new THREE.MeshStandardMaterial({
    color: 0x22c55e,
    emissive: 0x22c55e,
    emissiveIntensity: 0.25,
    roughness: 0.3,
    metalness: 0.6
});

const sphere = new THREE.Mesh(sphereGeometry, sphereMaterial);
scene.add(sphere);


let time = 0;
let isLoading = false;


function animate() {
    requestAnimationFrame(animate);
    time += 0.02;

    if (isLoading) {
        
        sphere.rotation.y += 0.08;
        sphere.rotation.x += 0.05;

        const pulse = 1 + Math.sin(time * 4) * 0.08;
        sphere.scale.set(pulse, pulse, pulse);
    } else {
        
        const breathe = 1 + Math.sin(time) * 0.04;
        sphere.scale.set(breathe, breathe, breathe);
        sphere.rotation.y += 0.002;
    }

    renderer.render(scene, camera);
}

animate();


function startLoading() {
    isLoading = true;
}

function stopLoading() {
    isLoading = false;
}

function updateRewardColor(reward) {
    let intensity = 0.2;

    if (reward >= 5) intensity = 0.5;
    else if (reward >= 3) intensity = 0.35;

    sphere.material.emissiveIntensity = intensity;
}

window.startLoading = startLoading;
window.stopLoading = stopLoading;
window.updateRewardColor = updateRewardColor;


window.addEventListener("resize", () => {
    camera.aspect = window.innerWidth / window.innerHeight;
    camera.updateProjectionMatrix();
    renderer.setSize(window.innerWidth, window.innerHeight, false);
});
