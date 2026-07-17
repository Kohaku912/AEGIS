import * as THREE from "three";
import { TOPOLOGY_POSITIONS } from "./SystemTopology";
import type { CognitiveScene, SceneRuntime, SceneTarget } from "./sceneTypes";

const STAGES = ["Observe", "Understand", "Plan", "Approve", "Execute", "Verify", "Complete"];

export function createMissionFlow(): {
  mission: THREE.Group;
  execution: THREE.Group;
  packets: THREE.Mesh[];
  approvalGate: THREE.Group;
  failureFragments: THREE.Group;
  recoveryPath: THREE.Group;
} {
  const mission = new THREE.Group();
  mission.name = "MissionFlowLayer";
  const pathPoints = STAGES.map((_, index) => new THREE.Vector3(-2.55 + index * 0.85, -2.05 + Math.sin(index * 0.8) * 0.12, -1.45 + index * 0.2));
  const curve = new THREE.CatmullRomCurve3(pathPoints);
  mission.add(new THREE.Mesh(
    new THREE.TubeGeometry(curve, 60, 0.03, 6, false),
    new THREE.MeshStandardMaterial({ color: 0x3d8bff, emissive: 0x102f68, transparent: true, opacity: 0.48 })
  ));
  pathPoints.forEach((point, index) => {
    const marker = new THREE.Mesh(
      new THREE.OctahedronGeometry(index === 3 ? 0.17 : 0.12, 0),
      new THREE.MeshStandardMaterial({ color: index === 3 ? 0xffb84d : 0x3d8bff, emissive: index === 3 ? 0x5f3b08 : 0x102c5a })
    );
    marker.position.copy(point);
    marker.name = `mission:${STAGES[index]}`;
    mission.add(marker);
  });

  const execution = new THREE.Group();
  execution.name = "ExecutionLayer";
  const packets = Array.from({ length: 7 }, (_, index) => {
    const packet = new THREE.Mesh(
      new THREE.BoxGeometry(0.11, 0.055, 0.2),
      new THREE.MeshStandardMaterial({ color: 0xffffff, emissive: 0x3d8bff, emissiveIntensity: 1.2, transparent: true })
    );
    packet.userData.phase = index / 7;
    packet.visible = false;
    execution.add(packet);
    return packet;
  });
  const approvalGate = new THREE.Group();
  approvalGate.name = "PolicyGate";
  const gate = new THREE.Mesh(
    new THREE.TorusGeometry(0.48, 0.045, 8, 40),
    new THREE.MeshStandardMaterial({ color: 0xffb84d, emissive: 0x7a4408, transparent: true, opacity: 0.88 })
  );
  gate.rotation.y = Math.PI / 2;
  approvalGate.add(gate);
  approvalGate.visible = false;
  execution.add(approvalGate);

  const failureFragments = new THREE.Group();
  failureFragments.name = "DiagnosticCutaway";
  for (let index = 0; index < 8; index += 1) {
    const fragment = new THREE.Mesh(
      new THREE.TetrahedronGeometry(0.08 + (index % 3) * 0.025, 0),
      new THREE.MeshStandardMaterial({ color: 0xff5d73, emissive: 0x5d101d, roughness: 0.48 })
    );
    fragment.position.set(Math.cos(index) * 0.55, Math.sin(index * 1.7) * 0.45, (index % 2 ? 1 : -1) * 0.22);
    failureFragments.add(fragment);
  }
  failureFragments.visible = false;
  execution.add(failureFragments);

  const recoveryPath = new THREE.Group();
  recoveryPath.name = "RecoveryPath";
  const recoveryCurve = new THREE.CatmullRomCurve3([
    new THREE.Vector3(-0.7, -0.35, 0.4),
    new THREE.Vector3(-0.25, 0.42, 0.1),
    new THREE.Vector3(0.35, -0.2, -0.05),
    new THREE.Vector3(0.8, 0.3, -0.25)
  ]);
  recoveryPath.add(new THREE.Mesh(
    new THREE.TubeGeometry(recoveryCurve, 40, 0.028, 6, false),
    new THREE.MeshStandardMaterial({ color: 0x2dd4a8, emissive: 0x12664e, transparent: true, opacity: 0.9 })
  ));
  recoveryPath.visible = false;
  execution.add(recoveryPath);
  return { mission, execution, packets, approvalGate, failureFragments, recoveryPath };
}

export function updateMissionFlow(runtime: SceneRuntime, target: SceneTarget, elapsed: number, delta: number): void {
  const active = target.scene === "executing" || target.scene === "observing" || target.scene === "planning";
  const targetPosition = new THREE.Vector3(...(TOPOLOGY_POSITIONS[target.activeServerId] || TOPOLOGY_POSITIONS["ai-server"]));
  const source = new THREE.Vector3(...TOPOLOGY_POSITIONS["ai-server"]);
  runtime.packets.forEach((packet, index) => {
    packet.visible = active;
    if (!active) return;
    const speed = 0.12 + target.activity * 0.38;
    const progress = target.reducedMotion ? (index + 1) / (runtime.packets.length + 1) : (elapsed * speed + Number(packet.userData.phase || 0)) % 1;
    packet.position.lerpVectors(source, targetPosition, progress);
    packet.lookAt(targetPosition);
    (packet.material as THREE.MeshStandardMaterial).opacity = THREE.MathUtils.damp((packet.material as THREE.MeshStandardMaterial).opacity, 0.45 + target.confidence * 0.55, 5, delta);
  });
  const gateVisible = target.scene === "approval";
  runtime.approvalGate.visible = gateVisible;
  if (gateVisible) {
    runtime.approvalGate.position.lerpVectors(source, targetPosition, 0.62);
    runtime.approvalGate.lookAt(targetPosition);
  }
  runtime.failureFragments.visible = target.scene === "critical";
  runtime.failureFragments.position.copy(targetPosition);
  runtime.recoveryPath.visible = target.scene === "recovery";
  runtime.recoveryPath.position.copy(targetPosition).multiplyScalar(0.55);
  runtime.mission.position.z = THREE.MathUtils.damp(runtime.mission.position.z, target.scene === "planning" ? 0.55 : 0, 3, delta);
}

export function missionStageForScene(scene: CognitiveScene): string {
  return {
    idle: "Ready",
    observing: "Observe",
    planning: "Plan",
    executing: "Execute",
    approval: "Approve",
    critical: "Diagnose",
    recovery: "Verify recovery",
    complete: "Complete"
  }[scene];
}
