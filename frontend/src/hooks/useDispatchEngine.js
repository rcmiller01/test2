import axios from 'axios';

export async function sendToDispatch({ input, emotion, persona, override }) {
  try {
    const payload = {
      input,
      emotion: emotion || "neutral",
      persona: persona || "auto",
      override: override || false
    };

    const response = await axios.post("/api/chat/dispatch", payload);
    return response.data;
  } catch (error) {
    console.error("Dispatch error:", error);
    return { persona: "system", response: "[Dispatch failed]" };
  }
}