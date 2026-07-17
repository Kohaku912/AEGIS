import * as THREE from "three";
import type { SceneTarget } from "./sceneTypes";

export function updateSceneCamera(camera: THREE.PerspectiveCamera, target: SceneTarget, delta: number): void {
  if (target.reducedMotion) {
    camera.position.copy(target.camera);
  } else {
    camera.position.x = THREE.MathUtils.damp(camera.position.x, target.camera.x, 2.8, delta);
    camera.position.y = THREE.MathUtils.damp(camera.position.y, target.camera.y, 2.8, delta);
    camera.position.z = THREE.MathUtils.damp(camera.position.z, target.camera.z, 2.8, delta);
  }
  camera.lookAt(target.focus);
}
