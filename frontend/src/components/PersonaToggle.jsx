import React, { useContext } from 'react';
import { PersonaContext } from '../context/PersonaContext';

export default function PersonaToggle() {
  const { mode, setMode } = useContext(PersonaContext);

  const toggleMode = () => {
    setMode(mode === 'companion' ? 'dev' : 'companion');
  };

  return (
    <div className="persona-toggle">
      <button onClick={toggleMode}>
        Mode: {mode === 'companion' ? 'Companion 🧘' : 'Dev 💻'}
      </button>
    </div>
  );
}