import { useState } from 'react';
import axios from 'axios';

const API_BASE = import.meta.env.VITE_GATEWAY_URL || 'http://localhost:5000';

export default function EmotionEval({ prompt, responseA, responseB }) {
  const [selection, setSelection] = useState(null);
  const [submitted, setSubmitted] = useState(false);

  const sendVote = async (winner) => {
    setSelection(winner);
    try {
      await axios.post(`${API_BASE}/api/vote_preference`, {
        prompt,
        response_a: responseA,
        response_b: responseB,
        winner,
      });
      setSubmitted(true);
    } catch (err) {
      console.error('Vote error', err);
    }
  };

  return (
    <div className="bg-gray-800 rounded-lg p-4 space-y-4">
      <h3 className="text-lg font-semibold">Emotion Eval Mode</h3>
      <p className="text-sm italic">{prompt}</p>
      <div className="grid grid-cols-2 gap-4">
        <div className={`p-3 rounded-lg ${selection === 'a' ? 'ring-2 ring-blue-500' : ''}`}>\
          <div className="text-sm mb-2">Response A</div>
          <div className="text-sm whitespace-pre-wrap">{responseA}</div>
          <button
            onClick={() => sendVote('a')}
            disabled={submitted}
            className="mt-2 px-3 py-1 rounded bg-blue-600 hover:bg-blue-500 disabled:opacity-50"
          >
            {selection === 'a' && submitted ? 'Voted' : 'Choose A'}
          </button>
        </div>
        <div className={`p-3 rounded-lg ${selection === 'b' ? 'ring-2 ring-blue-500' : ''}`}>\
          <div className="text-sm mb-2">Response B</div>
          <div className="text-sm whitespace-pre-wrap">{responseB}</div>
          <button
            onClick={() => sendVote('b')}
            disabled={submitted}
            className="mt-2 px-3 py-1 rounded bg-blue-600 hover:bg-blue-500 disabled:opacity-50"
          >
            {selection === 'b' && submitted ? 'Voted' : 'Choose B'}
          </button>
        </div>
      </div>
      {submitted && <p className="text-green-400">Vote recorded</p>}
    </div>
  );
}
