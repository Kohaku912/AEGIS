import * as THREE from "three";
import { TOPOLOGY_POSITIONS } from "./SystemTopology";
import type { VisualEvent } from "../../types";
import type { SceneTarget } from "./sceneTypes";

type ParticleRecord = { mesh: THREE.Mesh; eventId: string; startedAt: number; duration: number };

export function createEventParticleLayer(): THREE.Group {
  const group = new THREE.Group();
  group.name = "EventParticleLayer";
  group.userData.particles = [] as ParticleRecord[];
  return group;
}

export function updateEventParticles(group: THREE.Group, target: SceneTarget, now: number): void {
  const particles = group.userData.particles as ParticleRecord[];
  const known = new Set(particles.map((item) => item.eventId));
  for (const event of target.events) {
    if (known.has(event.id) || event.expiresAt <= now) continue;
    const record = createParticle(event, now);
    particles.push(record);
    group.add(record.mesh);
  }
  for (let index = particles.length - 1; index >= 0; index -= 1) {
    const record = particles[index];
    const progress = target.reducedMotion ? 0.7 : Math.min(1, (now - record.startedAt) / record.duration);
    const source = new THREE.Vector3(...(TOPOLOGY_POSITIONS[record.mesh.userData.serverId] || TOPOLOGY_POSITIONS["ai-server"]));
    const destination = new THREE.Vector3(...TOPOLOGY_POSITIONS["ai-server"]);
    record.mesh.position.lerpVectors(source, destination, progress);
    record.mesh.scale.setScalar(0.5 + Math.sin(progress * Math.PI) * 1.4);
    const material = record.mesh.material as THREE.MeshBasicMaterial;
    material.opacity = 1 - progress * 0.8;
    if (progress >= 1 || now - record.startedAt > record.duration) {
      group.remove(record.mesh);
      record.mesh.geometry.dispose();
      material.dispose();
      particles.splice(index, 1);
    }
  }
}

function createParticle(event: VisualEvent, now: number): ParticleRecord {
  const color = event.effect === "recovery" ? 0x2dd4a8 : event.effect === "fracture" || event.effect === "disconnect" ? 0xff5d73 : event.effect === "containment" ? 0xffb84d : event.effect === "complete" ? 0xffffff : 0x29d3ff;
  const mesh = new THREE.Mesh(
    event.effect === "fracture" ? new THREE.TetrahedronGeometry(0.1, 0) : new THREE.OctahedronGeometry(0.075, 0),
    new THREE.MeshBasicMaterial({ color, transparent: true, opacity: 0.95 })
  );
  mesh.userData.serverId = event.serverId;
  return { mesh, eventId: event.id, startedAt: now, duration: Math.max(500, event.expiresAt - event.createdAt) };
}
