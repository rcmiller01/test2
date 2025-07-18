import React, { createContext, useState } from 'react';

export const PersonaContext = createContext();

export const PersonaProvider = ({ children }) => {
  const [mode, setMode] = useState("companion");

  return (
    <PersonaContext.Provider value={{ mode, setMode }}>
      {children}
    </PersonaContext.Provider>
  );
};