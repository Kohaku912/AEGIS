import * as THREE from "three";
import type { SceneQuality } from "./sceneTypes";

export function createMemoryField(quality: SceneQuality): THREE.Group {
  const group = new THREE.Group();
  group.name = "MemoryFieldLayer";
  const bands = quality === "low" ? 2 : 4;
  for (let index = 0; index < bands; index += 1) {
    const y = 1.45 - index * 0.48;
    const curve = new THREE.CatmullRomCurve3([
      new THREE.Vector3(-3.7, y, -3.5 - index * 0.3),
      new THREE.Vector3(-1.8, y + 0.28, -2.9),
      new THREE.Vector3(0.25, y - 0.15, -2.5),
      new THREE.Vector3(2.8, y + 0.18, -3.2)
    ]);
    const geometry = new THREE.TubeGeometry(curve, 30, 0.018 + index * 0.004, 5, false);
    const material = new THREE.MeshStandardMaterial({
      color: index % 2 ? 0x8b7cff : 0xa66cff,
      emissive: index % 2 ? 0x2d235c : 0x3c1f5c,
      transparent: true,
      opacity: 0.24,
      roughness: 0.55,
      metalness: 0.12
    });
    group.add(new THREE.Mesh(geometry, material));
  }
  return group;
}
