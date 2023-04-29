import React, { Suspense, useRef } from "react";

import { Container, Jumbotron } from "reactstrap";

import { Section } from "./section";


import { Html, Canvas, useFrame } from "@react-three/fiber";

import {Model} from './init3D'

export default function ThreeD() {
  const ref = useRef();
  useFrame(() => (ref.current.rotation.y += 0.01));

  return (
    <Jumbotron>
      <Container>
        <Canvas colorManagment camera={{ position: [0, 0, 120], fov: 70 }} id='canvaId' >
          <ambientLight intensity={0.3} />
          <directionalLight position={[10, 10, 5]} intensity={1} />
          <directionalLight position={[0, 10, 0]} intensity={1.5} />
          <spotLight position={[1000, 0, 0]} intensity={1} />
          <Suspense fallback={null}>
            <Section factor={1.5} offset={1}>
              <group position={[0, 250, 0]}>
                <mesh ref={ref} position={[0, -35, 0]}>
                  <Model querySelectorId = 'canvaId' />
                </mesh>
                <Html fullscreen>
                  <div className="container">
                    <h1 className="title">Hello world!!</h1>
                  </div>
                </Html>
              </group>
            </Section>
          </Suspense>
        </Canvas>
      </Container>
    </Jumbotron>
  );
}
