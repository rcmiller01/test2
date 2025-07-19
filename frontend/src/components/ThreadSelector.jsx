import React, { useState, useEffect } from 'react';
import threads from '../conversations/index.json'; // Static import or fetch dynamically

export default function ThreadSelector({ currentThread, setCurrentThread }) {
  const handleChange = (e) => {
    setCurrentThread(e.target.value);
  };

  return (
    <div className="thread-selector">
      <label>Thread:</label>
      <select value={currentThread} onChange={handleChange}>
        {threads.map(thread => (
          <option key={thread.id} value={thread.id}>
            {thread.title}
          </option>
        ))}
      </select>
    </div>
  );
}