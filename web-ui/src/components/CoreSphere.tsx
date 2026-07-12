import { useEffect, useRef } from "react";
import * as THREE from "three";
import type { ServerItem } from "../types";

type Props = {
  mode: string;
  health: string;
  activityLevel: number;
  confidence: string;
  servers: ServerItem[];
};

export function CoreSphere({ mode, health, activityLevel, confidence, servers }: Props) {
  const mountRef = useRef<HTMLDivElement | null>(null);

  useEffect(() => {
    const mount = mountRef.current;
    if (!mount) return;
    const reducedMotion = window.matchMedia("(prefers-reduced-motion: reduce)").matches;
    const scene = new THREE.Scene();
    const camera = new THREE.PerspectiveCamera(42, mount.clientWidth / mount.clientHeight, 0.1, 100);
    camera.position.set(0, 0, 7.4);

    const renderer = new THREE.WebGLRenderer({ antialias: true, alpha: true });
    renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2));
    renderer.setSize(mount.clientWidth, mount.clientHeight);
    mount.appendChild(renderer.domElement);

    const coreColor = health === "OFFLINE" ? 0xff5d73 : health === "DEGRADED" ? 0xffb84d : 0x29d3ff;
    const shell = new THREE.Group();
    scene.add(shell);

    const sphere = new THREE.Mesh(
      new THREE.IcosahedronGeometry(1.25, 4),
      new THREE.MeshBasicMaterial({ color: coreColor, wireframe: true, transparent: true, opacity: 0.55 })
    );
    shell.add(sphere);

    const halo = new THREE.Mesh(
      new THREE.TorusGeometry(1.7, confidence === "low" ? 0.012 : 0.018, 12, 128),
      new THREE.MeshBasicMaterial({ color: confidence === "low" ? 0xffb84d : 0x8b7cff, transparent: true, opacity: 0.78 })
    );
    halo.rotation.x = Math.PI / 2.4;
    shell.add(halo);

    const orbitMaterial = new THREE.LineBasicMaterial({ color: 0x8ea0b8, transparent: true, opacity: 0.32 });
    for (let i = 0; i < 3; i += 1) {
      const curve = new THREE.EllipseCurve(0, 0, 2.05 + i * 0.34, 1.08 + i * 0.22, 0, Math.PI * 2);
      const points = curve.getPoints(96).map((p) => new THREE.Vector3(p.x, p.y, 0));
      const line = new THREE.Line(new THREE.BufferGeometry().setFromPoints(points), orbitMaterial);
      line.rotation.x = Math.PI / (2.6 + i * 0.35);
      line.rotation.y = i * 0.58;
      shell.add(line);
    }

    const serverGroup = new THREE.Group();
    const activeServers = servers.slice(0, 8);
    activeServers.forEach((server, index) => {
      const angle = (index / Math.max(activeServers.length, 1)) * Math.PI * 2;
      const radius = 2.9;
      const color = server.status === "ONLINE" ? 0x2dd4a8 : server.status === "DEGRADED" ? 0xffb84d : 0xff5d73;
      const node = new THREE.Mesh(new THREE.SphereGeometry(0.07, 16, 16), new THREE.MeshBasicMaterial({ color }));
      node.position.set(Math.cos(angle) * radius, Math.sin(angle) * 1.2, Math.sin(angle) * radius * 0.3);
      serverGroup.add(node);
      const line = new THREE.Line(
        new THREE.BufferGeometry().setFromPoints([new THREE.Vector3(0, 0, 0), node.position.clone()]),
        new THREE.LineBasicMaterial({ color, transparent: true, opacity: 0.28 })
      );
      serverGroup.add(line);
    });
    shell.add(serverGroup);

    const light = new THREE.PointLight(0xffffff, 1.1);
    light.position.set(0, 0, 4);
    scene.add(light);

    let frame = 0;
    const animate = () => {
      frame = requestAnimationFrame(animate);
      if (!reducedMotion) {
        const speed = 0.002 + Math.min(activityLevel, 4) * 0.0013;
        shell.rotation.y += speed;
        sphere.rotation.x += speed * 0.65;
        halo.rotation.z += speed * 0.45;
      }
      renderer.render(scene, camera);
    };
    animate();

    const resize = () => {
      if (!mount) return;
      camera.aspect = mount.clientWidth / mount.clientHeight;
      camera.updateProjectionMatrix();
      renderer.setSize(mount.clientWidth, mount.clientHeight);
    };
    window.addEventListener("resize", resize);

    return () => {
      cancelAnimationFrame(frame);
      window.removeEventListener("resize", resize);
      renderer.dispose();
      mount.removeChild(renderer.domElement);
    };
  }, [activityLevel, confidence, health, servers]);

  return (
    <div>
      <div ref={mountRef} className="core-canvas" role="img" aria-label={`AEGIS core sphere. Mode ${mode}, health ${health}.`} />
      <div className="muted mono" style={{ marginTop: 8 }}>
        Mode: {mode} / Health: {health} / Confidence: {confidence}
      </div>
    </div>
  );
}
