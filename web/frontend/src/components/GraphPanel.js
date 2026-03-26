//   web/frontend/src/components/GraphPanel.js

// ----- Imports -----
import React, { useEffect, useRef, useState } from 'react';
import * as THREE from 'three';
import './GraphPanel.css';

// ----- Helper Functions -----
// Define nodes (agents) and edges (interactions)
const nodes = [
  { id: 'coder', label: 'Coder', color: 0x4caf50 },
  { id: 'tester', label: 'Tester', color: 0xff9800 },
  { id: 'documenter', label: 'Documenter', color: 0x2196f3 },
  { id: 'reviewer', label: 'Reviewer', color: 0x9c27b0 },
  { id: 'executor', label: 'Executor', color: 0xf44336 },
  { id: 'manager', label: 'Manager', color: 0x00bcd4 }
];

const edges = [
  { from: 'coder', to: 'executor' },
  { from: 'tester', to: 'executor' },
  { from: 'documenter', to: 'executor' },
  { from: 'reviewer', to: 'executor' },
  { from: 'manager', to: 'coder' },
  { from: 'manager', to: 'tester' },
  { from: 'manager', to: 'documenter' },
  { from: 'manager', to: 'reviewer' },
  { from: 'manager', to: 'executor' }
];

// Simple circular layout for nodes
const positions = nodes.map((_, i) => {
  const angle = (i / nodes.length) * Math.PI * 2;
  const radius = 2.5;
  return {
    x: Math.cos(angle) * radius,
    y: Math.sin(angle) * radius,
    z: 0
  };
});

// ----- Main -----
function GraphPanel() {
  const [expanded, setExpanded] = useState(false);
  const mountRef = useRef(null);
  const sceneRef = useRef(null);
  const cameraRef = useRef(null);
  const rendererRef = useRef(null);
  const animationIdRef = useRef(null);

  // Initialize Three.js scene
  useEffect(() => {
    if (!mountRef.current) return;

    const width = mountRef.current.clientWidth;
    const height = 300; // fixed height when expanded

    const scene = new THREE.Scene();
    scene.background = new THREE.Color(0x111122);
    sceneRef.current = scene;

    const camera = new THREE.PerspectiveCamera(45, width / height, 0.1, 1000);
    camera.position.set(0, 0, 8);
    camera.lookAt(0, 0, 0);
    cameraRef.current = camera;

    const renderer = new THREE.WebGLRenderer({ antialias: true });
    renderer.setSize(width, height);
    renderer.setPixelRatio(window.devicePixelRatio);
    mountRef.current.appendChild(renderer.domElement);
    rendererRef.current = renderer;

    // Create node spheres
    const nodeObjects = nodes.map((node, idx) => {
      const geometry = new THREE.SphereGeometry(0.4, 32, 32);
      const material = new THREE.MeshStandardMaterial({ color: node.color, emissive: 0x222222 });
      const sphere = new THREE.Mesh(geometry, material);
      sphere.position.set(positions[idx].x, positions[idx].y, positions[idx].z);
      scene.add(sphere);
      return { sphere, label: node.label };
    });

    // Create edges (lines)
    const edgeMaterial = new THREE.LineBasicMaterial({ color: 0x88aaff });
    edges.forEach(edge => {
      const fromPos = positions[nodes.findIndex(n => n.id === edge.from)];
      const toPos = positions[nodes.findIndex(n => n.id === edge.to)];
      const points = [
        new THREE.Vector3(fromPos.x, fromPos.y, fromPos.z),
        new THREE.Vector3(toPos.x, toPos.y, toPos.z)
      ];
      const geometry = new THREE.BufferGeometry().setFromPoints(points);
      const line = new THREE.Line(geometry, edgeMaterial);
      scene.add(line);
    });

    // Add ambient and point lights
    const ambientLight = new THREE.AmbientLight(0x404060);
    scene.add(ambientLight);
    const pointLight = new THREE.PointLight(0xffffff, 1);
    pointLight.position.set(5, 5, 5);
    scene.add(pointLight);
    const backLight = new THREE.PointLight(0x88aaff, 0.5);
    backLight.position.set(-3, -2, -4);
    scene.add(backLight);

    // Animation loop
    const animate = () => {
      animationIdRef.current = requestAnimationFrame(animate);
      // Rotate the whole scene slightly
      scene.rotation.y += 0.003;
      scene.rotation.x += 0.001;
      renderer.render(scene, camera);
    };
    animate();

    // Handle window resize
    const handleResize = () => {
      if (!mountRef.current) return;
      const newWidth = mountRef.current.clientWidth;
      const newHeight = 300;
      camera.aspect = newWidth / newHeight;
      camera.updateProjectionMatrix();
      renderer.setSize(newWidth, newHeight);
    };
    window.addEventListener('resize', handleResize);

    return () => {
      window.removeEventListener('resize', handleResize);
      if (animationIdRef.current) cancelAnimationFrame(animationIdRef.current);
      if (rendererRef.current && mountRef.current) {
        mountRef.current.removeChild(rendererRef.current.domElement);
      }
      rendererRef.current?.dispose();
      sceneRef.current = null;
    };
  }, [expanded]); // re‑initialize when expanded changes (so size is correct)

  // Only render if expanded
  if (!expanded) {
    return (
      <div className="graph-panel-container collapsed">
        <button className="graph-panel-toggle" onClick={() => setExpanded(true)}>
          🧩 Show Agent Graph
        </button>
      </div>
    );
  }

  return (
    <div className="graph-panel-container expanded">
      <div className="graph-panel-header">
        <h3>Agent Orchestration Graph</h3>
        <button className="graph-panel-toggle" onClick={() => setExpanded(false)}>
          ✕ Hide
        </button>
      </div>
      <div ref={mountRef} className="graph-canvas" style={{ width: '100%', height: '300px' }} />
    </div>
  );
}

export default GraphPanel;