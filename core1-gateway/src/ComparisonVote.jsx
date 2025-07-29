import { useState } from 'react';
import axios from 'axios';

const API_BASE = import.meta.env.VITE_GATEWAY_URL || 'http://localhost:5000';

export default function ComparisonVote({ input, original, candidate }) {
  const [submitted, setSubmitted] = useState(false);
  const [error, setError] = useState('');

  const submitVote = async (winner) => {
    try {
      await axios.post(`${API_BASE}/api/vote_preference`, {
        input,
        response_a: original,
        response_b: candidate,
        winner,
      });
      setSubmitted(true);
    } catch (err) {
      setError('Failed to submit vote');
    }
  };

  if (submitted) {
    return <div className="bg-gray-800 p-4 rounded">Thanks for your feedback!</div>;
  }

  return (
    <div className="bg-gray-800 p-4 rounded space-y-4">
      <div className="text-sm text-gray-400">Which response do you prefer?</div>
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        <div className="p-3 rounded bg-gray-700">
          <div className="font-semibold mb-2">Response A</div>
          <pre className="whitespace-pre-wrap text-sm">{original}</pre>
          <button onClick={() => submitVote('a')} className="mt-2 bg-blue-600 px-3 py-1 rounded text-sm hover:bg-blue-500">Choose A</button>
        </div>
        <div className="p-3 rounded bg-gray-700">
          <div className="font-semibold mb-2">Response B</div>
          <pre className="whitespace-pre-wrap text-sm">{candidate}</pre>
          <button onClick={() => submitVote('b')} className="mt-2 bg-blue-600 px-3 py-1 rounded text-sm hover:bg-blue-500">Choose B</button>
        </div>
      </div>
      <button onClick={() => submitVote('skip')} className="text-xs text-gray-400 underline">Skip</button>
      {error && <div className="text-red-400 text-sm">{error}</div>}
    </div>
  );
}
