import { useEffect, useMemo, useRef, useState } from "react";
import * as THREE from "three";
import { EffectComposer } from "three/examples/jsm/postprocessing/EffectComposer.js";
import { RenderPass } from "three/examples/jsm/postprocessing/RenderPass.js";
import { UnrealBloomPass } from "three/examples/jsm/postprocessing/UnrealBloomPass.js";
import { createEnvironmentLayer } from "./EnvironmentLayer";
import { createEventParticleLayer, updateEventParticles } from "./EventParticles";
import { createMemoryField } from "./MemoryField";
import { createMissionFlow, missionStageForScene, updateMissionFlow } from "./MissionFlow";
import { updateSceneCamera } from "./SceneCamera";
import { detectSceneQuality, sceneFromProps, targetFromProps } from "./SceneDirector";
import { createSystemTopology, updateTopology } from "./SystemTopology";
import type { CognitiveFieldProps, SceneRuntime, SceneTarget } from "./sceneTypes";

export function CognitiveField(props: CognitiveFieldProps) {
  const hostRef = useRef<HTMLDivElement>(null);
  const reducedMotionRef = useRef(false);
  const targetRef = useRef<SceneTarget>(targetFromProps(props, false));
  const [quality, setQuality] = useState("high");
  const [reducedMotion, setReducedMotion] = useState(false);
  const scene = sceneFromProps(props);

  useEffect(() => {
    const media = window.matchMedia("(prefers-reduced-motion: reduce)");
    const update = () => {
      reducedMotionRef.current = media.matches;
      setReducedMotion(media.matches);
    };
    update();
    media.addEventListener("change", update);
    return () => media.removeEventListener("change", update);
  }, []);

  useEffect(() => {
    targetRef.current = targetFromProps(props, reducedMotionRef.current);
  }, [props]);

  useEffect(() => {
    const host = hostRef.current;
    if (!host) return;
    const selectedQuality = detectSceneQuality();
    setQuality(selectedQuality);
    const world = new THREE.Scene();
    world.fog = new THREE.FogExp2(0x05090f, 0.09);
    const camera = new THREE.PerspectiveCamera(38, 1, 0.1, 60);
    camera.position.set(0, 0.15, 8.4);
    const renderer = new THREE.WebGLRenderer({ antialias: selectedQuality !== "low", alpha: true, powerPreference: "high-performance" });
    renderer.setPixelRatio(Math.min(window.devicePixelRatio, selectedQuality === "high" ? 1.75 : 1.25));
    renderer.outputColorSpace = THREE.SRGBColorSpace;
    renderer.toneMapping = THREE.ACESFilmicToneMapping;
    renderer.toneMappingExposure = 0.88;
    renderer.domElement.dataset.sceneIdentity = "cognitive-field-v1";
    host.appendChild(renderer.domElement);

    const root = new THREE.Group();
    root.name = "AEGISScene";
    world.add(root);
    root.add(createEnvironmentLayer(selectedQuality));
    const memory = createMemoryField(selectedQuality);
    root.add(memory);
    const topology = createSystemTopology();
    root.add(topology.group);
    const missionParts = createMissionFlow();
    root.add(missionParts.mission, missionParts.execution);
    const eventLayer = createEventParticleLayer();
    root.add(eventLayer);

    world.add(new THREE.HemisphereLight(0x8aa7c7, 0x05090f, 1.25));
    const keyLight = new THREE.PointLight(0x8b7cff, 8, 18, 2);
    keyLight.position.set(-2, 3, 5);
    world.add(keyLight);
    const actionLight = new THREE.PointLight(0x29d3ff, 5, 15, 2);
    actionLight.position.set(3, -1, 4);
    world.add(actionLight);

    const runtime: SceneRuntime = {
      root,
      topology: topology.nodes,
      mission: missionParts.mission,
      execution: missionParts.execution,
      eventLayer,
      memory,
      cognition: topology.cognition,
      packets: missionParts.packets,
      approvalGate: missionParts.approvalGate,
      failureFragments: missionParts.failureFragments,
      recoveryPath: missionParts.recoveryPath
    };

    let composer: EffectComposer | undefined;
    let bloom: UnrealBloomPass | undefined;
    if (selectedQuality !== "low") {
      composer = new EffectComposer(renderer);
      composer.addPass(new RenderPass(world, camera));
      bloom = new UnrealBloomPass(new THREE.Vector2(1, 1), selectedQuality === "high" ? 0.42 : 0.25, 0.48, 0.86);
      composer.addPass(bloom);
    }

    const resize = () => {
      const width = Math.max(1, host.clientWidth);
      const height = Math.max(1, host.clientHeight);
      renderer.setSize(width, height, false);
      composer?.setSize(width, height);
      camera.aspect = width / height;
      camera.updateProjectionMatrix();
    };
    const observer = new ResizeObserver(resize);
    observer.observe(host);
    resize();

    const clock = new THREE.Clock();
    let raf = 0;
    let elapsed = 0;
    const animate = () => {
      const delta = Math.min(0.05, clock.getDelta());
      elapsed += delta;
      const target = targetRef.current;
      updateSceneCamera(camera, target, delta);
      updateTopology(runtime, target, delta);
      updateMissionFlow(runtime, target, elapsed, delta);
      updateEventParticles(eventLayer, target, Date.now());
      const cognitionMaterial = runtime.cognition.material as THREE.PointsMaterial;
      cognitionMaterial.opacity = THREE.MathUtils.damp(cognitionMaterial.opacity, 0.35 + target.confidence * 0.5, 4, delta);
      cognitionMaterial.size = THREE.MathUtils.damp(cognitionMaterial.size, target.scene === "planning" ? 0.07 : target.scene === "critical" ? 0.03 : 0.045, 4, delta);
      if (!target.reducedMotion) {
        const ambient = Math.sin(elapsed * Math.PI / 8) * 0.025;
        runtime.cognition.position.y = ambient;
        runtime.memory.position.x = Math.sin(elapsed * Math.PI / 10) * 0.04;
      }
      if (composer) composer.render(); else renderer.render(world, camera);
      raf = requestAnimationFrame(animate);
    };
    animate();

    return () => {
      cancelAnimationFrame(raf);
      observer.disconnect();
      world.traverse((object) => {
        const renderable = object as THREE.Mesh & { geometry?: THREE.BufferGeometry; material?: THREE.Material | THREE.Material[] };
        renderable.geometry?.dispose();
        if (Array.isArray(renderable.material)) renderable.material.forEach((material) => material.dispose());
        else renderable.material?.dispose();
      });
      composer?.dispose();
      bloom?.dispose();
      renderer.renderLists.dispose();
      renderer.dispose();
      renderer.domElement.remove();
    };
  }, []);

  const labels = useMemo(() => [
    ["browser-server", "Perception", "field-label--browser"],
    ["dev-server", "Development", "field-label--dev"],
    ["pc-server", "Physical action", "field-label--pc"],
    ["android-server", "Communication", "field-label--android"],
    ["room-server", "Environment", "field-label--room"],
    ["ai-server", "Cognition", "field-label--ai"]
  ] as const, []);

  return (
    <div
      className="cognitive-field"
      data-scene={scene}
      data-quality={quality}
      data-reduced-motion={reducedMotion}
      data-testid="cognitive-field"
    >
      <div className="cognitive-field__canvas core-canvas" ref={hostRef} role="img" aria-label={`AEGIS cognitive field. Scene ${scene}, health ${props.health}.`} />
      <div className="cognitive-field__horizon" aria-hidden="true">Context horizon / confidence {props.confidence}</div>
      {labels.map(([id, label, className]) => {
        const server = props.servers.find((item) => item.server_id === id);
        return (
          <div className={`field-label core-legend__item ${className}`} data-status={String(server?.status || "UNCONFIGURED").toUpperCase()} key={id}>
            <span>{label}</span>
            <strong>{id.replace("-server", "")}</strong>
            <small>{String(server?.status || "unconfigured")}</small>
          </div>
        );
      })}
      <div className="mission-depth-labels" aria-label="Mission lifecycle">
        <span data-state="past">Observe</span>
        <span data-state="current">{missionStageForScene(scene)}</span>
        <span data-state="next">{props.nextAction || "Verify"}</span>
      </div>
      <div className="cognitive-field__accessible-summary">
        <strong>{missionStageForScene(scene)}</strong>
        <span>{props.currentAction || "AEGIS is standing by."}</span>
        {props.approvalServerIds?.length ? <span>Execution is stopped at the policy gate for approval.</span> : null}
      </div>
    </div>
  );
}
