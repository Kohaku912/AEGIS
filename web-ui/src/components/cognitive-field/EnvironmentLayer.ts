import * as THREE from "three";
import type { SceneQuality } from "./sceneTypes";

export function createEnvironmentLayer(quality: SceneQuality): THREE.Group {
  const group = new THREE.Group();
  group.name = "EnvironmentLayer";
  const grid = new THREE.GridHelper(18, 28, 0x173247, 0x0b1b29);
  grid.position.set(0, -2.65, -2.8);
  grid.material.opacity = 0.24;
  grid.material.transparent = true;
  group.add(grid);

  const count = quality === "high" ? 220 : quality === "medium" ? 120 : 54;
  const positions = new Float32Array(count * 3);
  for (let index = 0; index < count; index += 1) {
    const seed = index * 12.9898;
    positions[index * 3] = Math.sin(seed) * 8;
    positions[index * 3 + 1] = Math.sin(seed * 0.37) * 4;
    positions[index * 3 + 2] = -2 - Math.abs(Math.cos(seed * 0.73) * 7);
  }
  const geometry = new THREE.BufferGeometry();
  geometry.setAttribute("position", new THREE.BufferAttribute(positions, 3));
  const material = new THREE.PointsMaterial({ color: 0x31516b, size: 0.026, transparent: true, opacity: 0.42, depthWrite: false });
  group.add(new THREE.Points(geometry, material));
  return group;
}
