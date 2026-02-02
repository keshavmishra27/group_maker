const canvas = document.getElementById("bg");

const scene = new THREE.Scene();
scene.background = new THREE.Color(0x05070f);

const camera = new THREE.PerspectiveCamera(
  60,
  window.innerWidth / window.innerHeight,
  0.1,
  1000
);

const renderer = new THREE.WebGLRenderer({
  canvas,
  antialias: true,
  alpha: true
});

renderer.setSize(window.innerWidth, window.innerHeight);
renderer.setPixelRatio(window.devicePixelRatio);

camera.position.z = 5;

// glowing sphere
const geometry = new THREE.SphereGeometry(1.2, 64, 64);
const material = new THREE.MeshStandardMaterial({
  color: 0x22c55e,
  emissive: 0x22c55e,
  emissiveIntensity: 0.4
});
const sphere = new THREE.Mesh(geometry, material);
scene.add(sphere);

// light
const light = new THREE.PointLight(0x22c55e, 2);
light.position.set(5, 5, 5);
scene.add(light);

function animate() {
  requestAnimationFrame(animate);
  sphere.rotation.y += 0.005;
  sphere.rotation.x += 0.003;
  renderer.render(scene, camera);
}

animate();

window.addEventListener("resize", () => {
  camera.aspect = window.innerWidth / window.innerHeight;
  camera.updateProjectionMatrix();
  renderer.setSize(window.innerWidth, window.innerHeight);
});
