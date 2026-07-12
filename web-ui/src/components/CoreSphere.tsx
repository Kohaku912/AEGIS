import { useEffect, useMemo, useRef } from "react";
import * as THREE from "three";
import { EffectComposer } from "three/examples/jsm/postprocessing/EffectComposer.js";
import { RenderPass } from "three/examples/jsm/postprocessing/RenderPass.js";
import { UnrealBloomPass } from "three/examples/jsm/postprocessing/UnrealBloomPass.js";
import { CORE_SERVER_IDS, serverLabel, type CoreServerId } from "../displayModel";
import type { ServerItem, VisualEvent } from "../types";

type Props = {
  mode: string;
  health: string;
  activityLevel: number;
  confidence: string;
  servers: ServerItem[];
  visualEvents: VisualEvent[];
  activeServerId?: string;
  nextServerId?: string;
  approvalServerIds?: string[];
};

type TargetState = {
  mode: string;
  health: string;
  activityLevel: number;
  confidence: string;
  servers: ServerItem[];
  events: VisualEvent[];
  activeServerId: string;
  nextServerIds: Set<string>;
  approvalServerIds: Set<string>;
};

type ArcRuntime = {
  serverId: CoreServerId;
  group: THREE.Group;
  segments: THREE.Mesh<THREE.TubeGeometry, THREE.MeshBasicMaterial>[];
  filaments: THREE.Mesh<THREE.TubeGeometry, THREE.MeshBasicMaterial>[];
  marker: THREE.Mesh<THREE.SphereGeometry, THREE.MeshBasicMaterial>;
  color: THREE.Color;
  targetColor: THREE.Color;
  opacity: number;
  targetOpacity: number;
};

const COLORS = {
  cyan: new THREE.Color("#29D3FF"),
  white: new THREE.Color("#EAF2FF"),
  violet: new THREE.Color("#8B7CFF"),
  amber: new THREE.Color("#FFB84D"),
  red: new THREE.Color("#FF5D73"),
  muted: new THREE.Color("#8EA0B8"),
  recovery: new THREE.Color("#2DD4A8")
};

export function CoreSphere({ mode, health, activityLevel, confidence, servers, visualEvents, activeServerId = "", nextServerId = "", approvalServerIds = [] }: Props) {
  const mountRef = useRef<HTMLDivElement | null>(null);
  const targetRef = useRef<TargetState>({
    mode,
    health,
    activityLevel,
    confidence,
    servers,
    events: visualEvents,
    activeServerId,
    nextServerIds: new Set(nextServerId ? [nextServerId] : []),
    approvalServerIds: new Set(approvalServerIds)
  });

  const legend = useMemo(() => CORE_SERVER_IDS.map((id) => ({ id, label: serverLabel(id) })), []);

  useEffect(() => {
    targetRef.current = {
      mode,
      health,
      activityLevel,
      confidence,
      servers,
      events: visualEvents,
      activeServerId,
      nextServerIds: new Set(nextServerId ? [nextServerId] : []),
      approvalServerIds: new Set(approvalServerIds)
    };
  }, [mode, health, activityLevel, confidence, servers, visualEvents, activeServerId, nextServerId, approvalServerIds]);

  useEffect(() => {
    const mount = mountRef.current;
    if (!mount) return;
    const reducedMotion = window.matchMedia("(prefers-reduced-motion: reduce)").matches;
    const scene = new THREE.Scene();
    const camera = new THREE.PerspectiveCamera(44, 1, 0.1, 100);
    camera.position.set(0, 0, 7.2);

    const renderer = new THREE.WebGLRenderer({ antialias: true, alpha: true, powerPreference: "high-performance" });
    renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2));
    renderer.outputColorSpace = THREE.SRGBColorSpace;
    mount.appendChild(renderer.domElement);

    const composer = new EffectComposer(renderer);
    composer.addPass(new RenderPass(scene, camera));
    const bloom = new UnrealBloomPass(new THREE.Vector2(1, 1), 0.38, 0.45, 0.86);
    composer.addPass(bloom);

    const shell = new THREE.Group();
    scene.add(shell);

    const coreMaterial = new THREE.ShaderMaterial({
      transparent: true,
      depthWrite: false,
      uniforms: {
        uTime: { value: 0 },
        uActivity: { value: 0.2 },
        uColor: { value: COLORS.cyan.clone() },
        uGlow: { value: 0.55 }
      },
      vertexShader: `
        uniform float uTime;
        uniform float uActivity;
        varying vec3 vNormal;
        varying vec3 vView;
        void main() {
          vNormal = normalize(normalMatrix * normal);
          vec3 displaced = position + normal * (sin(position.x * 4.7 + uTime * 1.4) + sin(position.y * 5.1 - uTime)) * 0.025 * uActivity;
          vec4 mvPosition = modelViewMatrix * vec4(displaced, 1.0);
          vView = normalize(-mvPosition.xyz);
          gl_Position = projectionMatrix * mvPosition;
        }
      `,
      fragmentShader: `
        uniform vec3 uColor;
        uniform float uGlow;
        varying vec3 vNormal;
        varying vec3 vView;
        void main() {
          float fresnel = pow(1.0 - max(dot(vNormal, vView), 0.0), 2.25);
          float core = 0.18 + fresnel * uGlow;
          gl_FragColor = vec4(uColor * core, 0.34 + fresnel * 0.42);
        }
      `
    });
    const core = new THREE.Mesh(new THREE.SphereGeometry(1.24, 96, 64), coreMaterial);
    shell.add(core);

    const containment = new THREE.Mesh(
      new THREE.TorusGeometry(1.72, 0.018, 12, 160),
      new THREE.MeshBasicMaterial({ color: COLORS.amber, transparent: true, opacity: 0 })
    );
    containment.rotation.x = Math.PI / 2.15;
    shell.add(containment);

    const recoveryWave = new THREE.Mesh(
      new THREE.TorusGeometry(1.35, 0.015, 12, 160),
      new THREE.MeshBasicMaterial({ color: COLORS.recovery, transparent: true, opacity: 0 })
    );
    recoveryWave.rotation.x = Math.PI / 2;
    shell.add(recoveryWave);

    const arcs = new Map<CoreServerId, ArcRuntime>();
    CORE_SERVER_IDS.forEach((serverId, index) => {
      const arc = createServerArc(serverId, index);
      arcs.set(serverId, arc);
      shell.add(arc.group);
    });

    scene.add(new THREE.AmbientLight(0x8ea0b8, 0.55));
    const light = new THREE.PointLight(0xeaf2ff, 1.3);
    light.position.set(0, 0, 4.8);
    scene.add(light);

    const clock = new THREE.Clock();
    const resize = () => {
      const width = Math.max(1, mount.clientWidth);
      const height = Math.max(1, mount.clientHeight);
      camera.aspect = width / height;
      camera.updateProjectionMatrix();
      renderer.setSize(width, height, false);
      composer.setSize(width, height);
      bloom.resolution.set(width, height);
    };
    const observer = new ResizeObserver(resize);
    observer.observe(mount);
    resize();

    let raf = 0;
    const animate = () => {
      raf = requestAnimationFrame(animate);
      const delta = Math.min(clock.getDelta(), 0.05);
      const now = performance.now();
      const target = targetRef.current;
      const activity = Math.min(Math.max(Number(target.activityLevel || 1), 0), 8) / 8;
      const speedTarget = reducedMotion ? 0 : 0.08 + activity * 0.42;
      shell.userData.rotationSpeed = THREE.MathUtils.damp(Number(shell.userData.rotationSpeed || 0), speedTarget, 2.6, delta);
      shell.rotation.y += Number(shell.userData.rotationSpeed) * delta;
      core.rotation.x += Number(shell.userData.rotationSpeed) * delta * 0.42;

      coreMaterial.uniforms.uTime.value += delta;
      coreMaterial.uniforms.uActivity.value = THREE.MathUtils.damp(coreMaterial.uniforms.uActivity.value, 0.25 + activity, 3.2, delta);
      coreMaterial.uniforms.uGlow.value = THREE.MathUtils.damp(coreMaterial.uniforms.uGlow.value, target.health === "DEGRADED" ? 0.9 : target.health === "OFFLINE" ? 0.35 : 0.62, 2.5, delta);
      (coreMaterial.uniforms.uColor.value as THREE.Color).lerp(target.health === "OFFLINE" ? COLORS.red : target.health === "DEGRADED" ? COLORS.amber : COLORS.cyan, 1 - Math.exp(-delta * 2.8));
      const breath = reducedMotion ? 1 : 1 + Math.sin(now * 0.0016) * (0.018 + activity * 0.018);
      core.scale.setScalar(breath);

      const activeEvents = target.events.filter((event) => event.expiresAt > Date.now());
      let containmentOpacity = 0;
      let recoveryOpacity = 0;
      for (const arc of arcs.values()) {
        updateArcTargets(arc, target, activeEvents, now);
        arc.color.lerp(arc.targetColor, 1 - Math.exp(-delta * 5.5));
        arc.opacity = THREE.MathUtils.damp(arc.opacity, arc.targetOpacity, 5.5, delta);
        for (const mesh of [...arc.segments, ...arc.filaments]) {
          const material = mesh.material;
          material.color.copy(arc.color);
          const mid = (mesh.userData.mid as THREE.Vector3).clone();
          mid.applyMatrix4(shell.matrixWorld);
          const depthFade = mid.z >= 0 ? 1 : 0.34;
          material.opacity = arc.opacity * depthFade * Number(mesh.userData.opacityScale || 1);
          mesh.visible = Boolean(mesh.userData.enabled);
        }
        arc.marker.material.color.copy(arc.color);
        arc.marker.material.opacity = Math.min(1, arc.opacity + 0.25);
        arc.group.scale.setScalar(THREE.MathUtils.damp(arc.group.scale.x, Number(arc.group.userData.targetScale || 1), 8, delta));
        if (arc.group.userData.containment) containmentOpacity = Math.max(containmentOpacity, Number(arc.group.userData.effectStrength || 0));
        if (arc.group.userData.recovery) recoveryOpacity = Math.max(recoveryOpacity, Number(arc.group.userData.effectStrength || 0));
      }
      containment.material.opacity = THREE.MathUtils.damp(containment.material.opacity, Math.min(0.58, containmentOpacity), 6, delta);
      recoveryWave.material.opacity = THREE.MathUtils.damp(recoveryWave.material.opacity, Math.min(0.72, recoveryOpacity), 5, delta);
      recoveryWave.scale.setScalar(1 + recoveryOpacity * 1.25);
      if (!reducedMotion) recoveryWave.rotation.z += delta * 1.2;
      camera.position.z = THREE.MathUtils.damp(camera.position.z, target.mode === "EXECUTING" ? 6.6 : 7.25, 1.8, delta);
      composer.render();
    };
    animate();

    return () => {
      cancelAnimationFrame(raf);
      observer.disconnect();
      composer.dispose();
      disposeObject(scene);
      renderer.dispose();
      renderer.domElement.remove();
    };
  }, []);

  return (
    <div className="core-sphere" data-testid="core-sphere" data-mode={mode} data-health={health}>
      <div ref={mountRef} className="core-canvas" role="img" aria-label={`AEGIS core sphere. Mode ${mode}, health ${health}.`} />
      <div className="core-legend" aria-label="Core server arcs">
        {legend.map((item) => (
          <span className="core-legend__item" data-server={item.id} key={item.id}>
            <i aria-hidden="true" />
            {item.label}
          </span>
        ))}
      </div>
      <div className="muted mono core-caption">
        Mode: {mode} / Health: {health} / Confidence: {confidence}
      </div>
    </div>
  );
}

function createServerArc(serverId: CoreServerId, index: number): ArcRuntime {
  const group = new THREE.Group();
  group.rotation.set(index * 0.37, index * 0.71, index * 0.23);
  const radius = 2.05;
  const offset = (index / CORE_SERVER_IDS.length) * Math.PI;
  const segments = [
    makeTube(radius, offset + 0.1, offset + Math.PI * 0.68, 0.018),
    makeTube(radius, offset + Math.PI * 0.78, offset + Math.PI * 1.34, 0.018),
    makeTube(radius, offset + Math.PI * 1.46, offset + Math.PI * 2 - 0.1, 0.018)
  ];
  const filamentA = makeTube(radius + 0.16, offset + 0.25, offset + Math.PI * 1.75, 0.006);
  const filamentB = makeTube(radius - 0.17, offset + Math.PI * 0.08, offset + Math.PI * 1.92, 0.005);
  filamentA.rotation.x = 0.18;
  filamentB.rotation.y = -0.14;
  const marker = new THREE.Mesh(
    new THREE.SphereGeometry(0.055, 20, 20),
    new THREE.MeshBasicMaterial({ color: COLORS.cyan, transparent: true, opacity: 0.8 })
  );
  marker.position.copy(pointOnCircle(radius + 0.07, offset + index * 0.24));
  for (const mesh of [...segments, filamentA, filamentB, marker]) group.add(mesh);
  return {
    serverId,
    group,
    segments,
    filaments: [filamentA, filamentB],
    marker,
    color: COLORS.cyan.clone(),
    targetColor: COLORS.cyan.clone(),
    opacity: 0.42,
    targetOpacity: 0.42
  };
}

function makeTube(radius: number, start: number, end: number, tubeRadius: number) {
  const points: THREE.Vector3[] = [];
  const steps = 64;
  for (let i = 0; i <= steps; i += 1) {
    const t = start + ((end - start) * i) / steps;
    points.push(pointOnCircle(radius, t));
  }
  const curve = new THREE.CatmullRomCurve3(points);
  const geometry = new THREE.TubeGeometry(curve, 72, tubeRadius, 8, false);
  const material = new THREE.MeshBasicMaterial({ color: COLORS.cyan, transparent: true, opacity: 0.4, depthWrite: false });
  const mesh = new THREE.Mesh(geometry, material);
  mesh.userData.mid = pointOnCircle(radius, (start + end) / 2);
  mesh.userData.enabled = true;
  mesh.userData.opacityScale = tubeRadius < 0.01 ? 0.42 : 1;
  return mesh;
}

function pointOnCircle(radius: number, t: number) {
  return new THREE.Vector3(Math.cos(t) * radius, Math.sin(t) * radius, Math.sin(t * 1.7) * 0.18);
}

function updateArcTargets(arc: ArcRuntime, target: TargetState, activeEvents: VisualEvent[], now: number) {
  const server = target.servers.find((item) => item.server_id === arc.serverId);
  const status = String(server?.status || "UNCONFIGURED").toUpperCase();
  const event = activeEvents.find((item) => item.serverId === arc.serverId);
  const age = event ? Math.max(0, Math.min(1, (event.expiresAt - Date.now()) / Math.max(1, event.expiresAt - event.createdAt))) : 0;
  arc.group.userData.targetScale = 1;
  arc.group.userData.effectStrength = age;
  arc.group.userData.containment = false;
  arc.group.userData.recovery = false;
  arc.targetColor.copy(COLORS.cyan);
  arc.targetOpacity = 0.5;
  arc.segments.forEach((segment) => { segment.userData.enabled = true; });

  if (status === "UNCONFIGURED" || status === "DISABLED") {
    arc.targetColor.copy(COLORS.muted);
    arc.targetOpacity = 0.22;
  }
  if (status === "OFFLINE") {
    arc.targetColor.copy(COLORS.muted);
    arc.targetOpacity = 0.26;
    arc.segments[1].userData.enabled = false;
  }
  if (status === "DEGRADED") {
    arc.targetColor.copy(COLORS.amber);
    arc.targetOpacity = 0.58 + Math.sin(now * 0.018) * 0.08;
  }
  if (target.nextServerIds.has(arc.serverId)) {
    arc.targetColor.copy(COLORS.violet);
    arc.targetOpacity = 0.72;
  }
  if (target.approvalServerIds.has(arc.serverId)) {
    arc.targetColor.copy(COLORS.amber);
    arc.targetOpacity = 0.86;
    arc.group.userData.containment = true;
  }
  if (target.activeServerId === arc.serverId) {
    arc.targetColor.copy(COLORS.white).lerp(COLORS.cyan, 0.28);
    arc.targetOpacity = 0.94;
    arc.group.userData.targetScale = 1.02;
  }
  if (event) {
    if (event.effect === "fracture") {
      arc.targetColor.copy(COLORS.red);
      arc.targetOpacity = 0.96;
      arc.group.userData.targetScale = 1 + age * 0.04;
    } else if (event.effect === "containment") {
      arc.targetColor.copy(COLORS.amber);
      arc.group.userData.containment = true;
      arc.targetOpacity = 0.96;
    } else if (event.effect === "recovery") {
      arc.targetColor.copy(COLORS.recovery);
      arc.group.userData.recovery = true;
      arc.targetOpacity = 0.98;
    } else if (event.effect === "complete" || event.effect === "pulse") {
      arc.targetColor.copy(COLORS.white).lerp(COLORS.cyan, 0.2);
      arc.targetOpacity = 0.86 + age * 0.14;
      arc.group.userData.targetScale = 1 + age * 0.035;
    } else if (event.effect === "disconnect") {
      arc.segments[1].userData.enabled = false;
      arc.targetColor.copy(COLORS.red);
      arc.targetOpacity = 0.64;
    }
  }
}

function disposeObject(object: THREE.Object3D) {
  object.traverse((child) => {
    const mesh = child as THREE.Mesh;
    if (mesh.geometry) mesh.geometry.dispose();
    const material = mesh.material as THREE.Material | THREE.Material[] | undefined;
    if (Array.isArray(material)) material.forEach((item) => item.dispose());
    else if (material) material.dispose();
  });
}
