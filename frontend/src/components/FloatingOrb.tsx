import { useRef, useMemo } from 'react';
import { Canvas, useFrame } from '@react-three/fiber';
import { Sphere, MeshDistortMaterial } from '@react-three/drei';
import * as THREE from 'three';

interface AnimatedOrbProps {
  emotion?: 'calm' | 'stressed' | 'sad' | 'happy' | 'neutral';
  mousePos: { x: number; y: number };
}

const Particles = ({ emotion = 'calm' }: { emotion?: string }) => {
  const particlesRef = useRef<THREE.Points>(null);
  
  const particles = useMemo(() => {
    const particleCount = 50;
    const positions = new Float32Array(particleCount * 3);
    
    for (let i = 0; i < particleCount; i++) {
      positions[i * 3] = (Math.random() - 0.5) * 10;
      positions[i * 3 + 1] = (Math.random() - 0.5) * 10;
      positions[i * 3 + 2] = (Math.random() - 0.5) * 10;
    }
    
    return positions;
  }, []);

  useFrame((state) => {
    if (!particlesRef.current) return;
    const time = state.clock.getElapsedTime();
    particlesRef.current.rotation.y = time * 0.05;
    
    const positions = particlesRef.current.geometry.attributes.position.array as Float32Array;
    for (let i = 0; i < positions.length; i += 3) {
      positions[i + 1] += Math.sin(time + positions[i]) * 0.001;
    }
    particlesRef.current.geometry.attributes.position.needsUpdate = true;
  });

  return (
    <points ref={particlesRef}>
      <bufferGeometry>
        <bufferAttribute
          attach="attributes-position"
          count={particles.length / 3}
          array={particles}
          itemSize={3}
        />
      </bufferGeometry>
      <pointsMaterial
        size={0.05}
        color="#2DD4BF"
        transparent
        opacity={0.3}
        sizeAttenuation
        blending={THREE.AdditiveBlending}
      />
    </points>
  );
};

const AnimatedOrb = ({ emotion = 'calm', mousePos }: AnimatedOrbProps) => {
  const meshRef = useRef<THREE.Mesh>(null);

  const emotionColors = {
    calm: '#2DD4BF',
    stressed: '#EF4444',
    sad: '#60A5FA',
    happy: '#FACC15',
    neutral: '#A78BFA',
  };

  const emotionSpeeds = {
    calm: 2,
    stressed: 4,
    sad: 1.5,
    happy: 5,
    neutral: 2.5,
  };

  useFrame((state) => {
    if (!meshRef.current) return;
    
    const time = state.clock.getElapsedTime();
    
    // Gentle breathing animation
    const breathingScale = 2.5 + Math.sin(time * 0.5) * 0.15;
    meshRef.current.scale.setScalar(breathingScale);
    
    // Gentle rotation
    meshRef.current.rotation.x = time * 0.1;
    meshRef.current.rotation.y = time * 0.15;
    
    // Stressed emotion has slight shake
    if (emotion === 'stressed') {
      meshRef.current.position.x = mousePos.x * 2 + Math.sin(time * 10) * 0.02;
      meshRef.current.position.y = mousePos.y * 2 + Math.cos(time * 10) * 0.02;
    } else {
      // Smooth mouse interaction
      meshRef.current.position.x = THREE.MathUtils.lerp(
        meshRef.current.position.x,
        mousePos.x * 1.5,
        0.05
      );
      meshRef.current.position.y = THREE.MathUtils.lerp(
        meshRef.current.position.y,
        mousePos.y * 1.5,
        0.05
      );
    }
  });

  return (
    <>
      <Sphere ref={meshRef} args={[1, 100, 100]}>
        <MeshDistortMaterial
          color={emotionColors[emotion]}
          attach="material"
          distort={0.4}
          speed={emotionSpeeds[emotion]}
          roughness={0.2}
          metalness={0.8}
        />
      </Sphere>
      <pointLight
        position={[0, 0, 0]}
        color={emotionColors[emotion]}
        intensity={2}
        distance={10}
      />
    </>
  );
};

interface FloatingOrbProps {
  emotion?: 'calm' | 'stressed' | 'sad' | 'happy' | 'neutral';
}

const FloatingOrb = ({ emotion = 'calm' }: FloatingOrbProps) => {
  const mousePos = useRef({ x: 0, y: 0 });

  const handleMouseMove = (e: React.MouseEvent<HTMLDivElement>) => {
    const rect = e.currentTarget.getBoundingClientRect();
    const x = (e.clientX - rect.left) / rect.width - 0.5;
    const y = -((e.clientY - rect.top) / rect.height - 0.5);
    mousePos.current = { x, y };
  };

  return (
    <div 
      className="w-full h-[500px] relative"
      onMouseMove={handleMouseMove}
    >
      <Canvas camera={{ position: [0, 0, 8], fov: 45 }}>
        <ambientLight intensity={0.3} />
        <hemisphereLight intensity={0.4} groundColor="#000000" />
        <spotLight position={[10, 10, 10]} angle={0.3} intensity={0.5} penumbra={1} />
        <spotLight position={[-10, -10, -10]} angle={0.3} intensity={0.3} penumbra={1} color="#A78BFA" />
        <AnimatedOrb emotion={emotion} mousePos={mousePos.current} />
        <Particles emotion={emotion} />
      </Canvas>
    </div>
  );
};

export default FloatingOrb;
