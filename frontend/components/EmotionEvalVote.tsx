import React, { useState } from 'react';

interface EmotionEvalVoteProps {
  prompt: string;
  responseA: string;
  responseB: string;
  onVoted?: () => void;
}

export const EmotionEvalVote: React.FC<EmotionEvalVoteProps> = ({ prompt, responseA, responseB, onVoted }) => {
  const [winner, setWinner] = useState<'a' | 'b' | ''>('');
  const [submitting, setSubmitting] = useState(false);

  const submitVote = async () => {
    if (!winner) return;
    setSubmitting(true);
    try {
      await fetch('/api/vote_preference', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          prompt,
          response_a: responseA,
          response_b: responseB,
          winner,
        }),
      });
      if (onVoted) onVoted();
    } finally {
      setSubmitting(false);
    }
  };

  return (
    <div className="emotion-eval-vote">
      <p className="prompt">{prompt}</p>
      <div className="responses">
        <label>
          <input type="radio" name="vote" disabled={submitting} onChange={() => setWinner('a')} />
          <span>A: {responseA}</span>
        </label>
        <label>
          <input type="radio" name="vote" disabled={submitting} onChange={() => setWinner('b')} />
          <span>B: {responseB}</span>
        </label>
      </div>
      <button onClick={submitVote} disabled={!winner || submitting}>Submit</button>
    </div>
  );
};

export default EmotionEvalVote;
