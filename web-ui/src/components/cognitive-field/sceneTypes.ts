import type * as THREE from "three";
import type { ServerItem, VisualEvent } from "../../types";

export type SceneQuality = "high" | "medium" | "low";
export type CognitiveScene = "idle" | "observing" | "planning" | "executing" | "approval" | "critical" | "recovery" | "complete";

export type CognitiveFieldProps = {
  mode: string;
  health: string;
  activityLevel: number;
  confidence: string;
  servers: ServerItem[];
  visualEvents: VisualEvent[];
  activeServerId?: string;
  nextServerId?: string;
  approvalServerIds?: string[];
  currentAction?: string;
  nextAction?: string;
};

export type SceneTarget = {
  scene: CognitiveScene;
  activity: number;
  confidence: number;
  camera: THREE.Vector3;
  focus: THREE.Vector3;
  activeServerId: string;
  nextServerId: string;
  approvalServerIds: string[];
  servers: ServerItem[];
  events: VisualEvent[];
  reducedMotion: boolean;
};

export type TopologyNode = {
  id: string;
  group: THREE.Group;
  plate: THREE.Mesh;
  position: THREE.Vector3;
};

export type SceneRuntime = {
  root: THREE.Group;
  topology: Map<string, TopologyNode>;
  mission: THREE.Group;
  execution: THREE.Group;
  eventLayer: THREE.Group;
  memory: THREE.Group;
  cognition: THREE.Points;
  packets: THREE.Mesh[];
  approvalGate: THREE.Group;
  failureFragments: THREE.Group;
  recoveryPath: THREE.Group;
};
