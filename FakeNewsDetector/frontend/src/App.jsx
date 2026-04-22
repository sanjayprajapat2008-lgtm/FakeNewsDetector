import { Canvas } from '@react-three/fiber';
import Background3D from './components/Background3D';
import DetectorForm from './components/DetectorForm';
import './index.css';

function App() {
  return (
    <div className="app-container">
      <div className="canvas-container">
        <Canvas camera={{ position: [0, 0, 5], fov: 45 }}>
          <Background3D />
        </Canvas>
      </div>
      
      <div className="ui-container">
        <DetectorForm />
      </div>
    </div>
  );
}

export default App;
