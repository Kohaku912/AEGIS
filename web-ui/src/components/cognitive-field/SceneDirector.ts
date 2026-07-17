import * as THREE from "three";
import type { CognitiveFieldProps, CognitiveScene, SceneQuality, SceneTarget } from "./sceneTypes";

export function sceneFromProps(props: CognitiveFieldProps): CognitiveScene {
  const mode = props.mode.toLowerCase();
  const health = props.health.toLowerCase();
  if (health.includes("critical") || health.includes("error")) return "critical";
  if (props.visualEvents.some((event) => event.effect === "recovery")) return "recovery";
  if (props.visualEvents.some((event) => event.effect === "fracture" || event.effect === "disconnect")) return "critical";
  if (props.approvalServerIds?.length || mode.includes("approval") || mode.includes("waiting")) return "approval";
  if (mode.includes("observ")) return "observing";
  if (mode.includes("plan")) return "planning";
  if (mode.includes("execut") || props.activeServerId) return "executing";
  if (mode.includes("complete")) return "complete";
  return "idle";
}

export function targetFromProps(props: CognitiveFieldProps, reducedMotion: boolean): SceneTarget {
  const scene = sceneFromProps(props);
  const cameraByScene: Record<CognitiveScene, THREE.Vector3> = {
    idle: new THREE.Vector3(0, 0.15, 7.25),
    observing: new THREE.Vector3(-0.48, 0.25, 6.65),
    planning: new THREE.Vector3(0, 0.42, 7.75),
    executing: new THREE.Vector3(0.38, 0.12, 6.1),
    approval: new THREE.Vector3(0.08, 0.04, 5.8),
    critical: new THREE.Vector3(0.58, 0.3, 5.55),
    recovery: new THREE.Vector3(0.2, 0.24, 6.45),
    complete: new THREE.Vector3(0, 0.18, 7.05)
  };
  return {
    scene,
    activity: THREE.MathUtils.clamp(props.activityLevel / 6, 0.08, 1),
    confidence: confidenceValue(props.confidence),
    camera: cameraByScene[scene],
    focus: new THREE.Vector3(scene === "critical" ? 0.7 : 0, scene === "approval" ? -0.1 : 0, 0),
    activeServerId: props.activeServerId || "",
    nextServerId: props.nextServerId || "",
    approvalServerIds: props.approvalServerIds || [],
    servers: props.servers,
    events: props.visualEvents,
    reducedMotion
  };
}

export function detectSceneQuality(): SceneQuality {
  const cores = navigator.hardwareConcurrency || 4;
  const memory = Number((navigator as Navigator & { deviceMemory?: number }).deviceMemory || 4);
  if (cores <= 4 || memory <= 4 || window.innerWidth < 1000) return "low";
  if (cores <= 8 || memory <= 8) return "medium";
  return "high";
}

function confidenceValue(confidence: string): number {
  const value = confidence.toLowerCase();
  if (value === "high") return 1;
  if (value === "low") return 0.38;
  return 0.68;
}
