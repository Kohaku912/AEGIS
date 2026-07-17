import * as THREE from "three";
import type { SceneRuntime, TopologyNode } from "./sceneTypes";

export const TOPOLOGY_POSITIONS: Record<string, [number, number, number]> = {
  "ai-server": [0, 0.15, -0.2],
  "browser-server": [-2.85, 1.2, -1.55],
  "pc-server": [-2.7, -1.25, 0.65],
  "android-server": [2.75, -1.0, 0.5],
  "room-server": [2.9, 1.05, -1.8],
  "dev-server": [0.15, 2.05, -1.05]
};

export function createSystemTopology(): { group: THREE.Group; nodes: Map<string, TopologyNode>; cognition: THREE.Points } {
  const group = new THREE.Group();
  group.name = "SystemTopologyLayer";
  const nodes = new Map<string, TopologyNode>();
  const center = new THREE.Vector3(...TOPOLOGY_POSITIONS["ai-server"]);
  for (const [id, rawPosition] of Object.entries(TOPOLOGY_POSITIONS)) {
    const position = new THREE.Vector3(...rawPosition);
    const nodeGroup = new THREE.Group();
    nodeGroup.position.copy(position);
    nodeGroup.name = id;
    const nodeRadius = id === "ai-server" ? 0.54 : 0.38;
    const geometry = new THREE.CylinderGeometry(nodeRadius, nodeRadius, 0.14, 6);
    geometry.rotateX(Math.PI / 2);
    const material = new THREE.MeshStandardMaterial({ color: 0x31c7b5, emissive: 0x0a3a3a, roughness: 0.34, metalness: 0.48, transparent: true, opacity: 0.86 });
    const plate = new THREE.Mesh(geometry, material);
    nodeGroup.add(plate);
    if (id !== "ai-server") {
      const path = new THREE.LineCurve3(center, position);
      const route = new THREE.Mesh(
        new THREE.TubeGeometry(path, 24, 0.022, 6, false),
        new THREE.MeshStandardMaterial({ color: 0x315d68, emissive: 0x0b2630, transparent: true, opacity: 0.34 })
      );
      group.add(route);
    }
    group.add(nodeGroup);
    nodes.set(id, { id, group: nodeGroup, plate, position });
  }

  const cognitionGeometry = new THREE.BufferGeometry();
  const positions = new Float32Array(240 * 3);
  for (let index = 0; index < 240; index += 1) {
    const angle = index * 2.399963;
    const radius = 0.18 + ((index * 17) % 97) / 112;
    positions[index * 3] = Math.cos(angle) * radius;
    positions[index * 3 + 1] = Math.sin(angle) * radius * 0.7 + 0.15;
    positions[index * 3 + 2] = Math.sin(index * 0.71) * 0.45 - 0.2;
  }
  cognitionGeometry.setAttribute("position", new THREE.BufferAttribute(positions, 3));
  const cognition = new THREE.Points(cognitionGeometry, new THREE.PointsMaterial({ color: 0x8b7cff, size: 0.064, transparent: true, opacity: 0.76, depthWrite: false, blending: THREE.AdditiveBlending }));
  cognition.name = "CognitiveFieldLayer";
  group.add(cognition);
  return { group, nodes, cognition };
}

export function updateTopology(runtime: SceneRuntime, target: import("./sceneTypes").SceneTarget, delta: number): void {
  const statusById = new Map(target.servers.map((server) => [server.server_id, String(server.status || "").toUpperCase()]));
  runtime.topology.forEach((node, id) => {
    const material = node.plate.material as THREE.MeshStandardMaterial;
    const status = statusById.get(id) || "UNCONFIGURED";
    const isActive = id === target.activeServerId;
    const isNext = id === target.nextServerId;
    const isApproval = target.approvalServerIds.includes(id);
    const targetColor = new THREE.Color(
      status === "OFFLINE" ? 0x5d2630 : status === "DEGRADED" ? 0x9f6c22 : isApproval ? 0xffb84d : isNext ? 0x8b7cff : isActive ? 0x3d8bff : 0x31c7b5
    );
    material.color.lerp(targetColor, 1 - Math.exp(-delta * 5));
    material.emissive.lerp(targetColor.clone().multiplyScalar(isActive || isApproval ? 0.38 : 0.12), 1 - Math.exp(-delta * 4));
    material.opacity = THREE.MathUtils.damp(material.opacity, status === "OFFLINE" ? 0.16 : isActive ? 1 : 0.78, 5, delta);
    const scale = isActive ? 1.22 : isNext ? 1.1 : 1;
    node.group.scale.setScalar(THREE.MathUtils.damp(node.group.scale.x, scale, 5, delta));
  });
}
