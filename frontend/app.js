const inputBox = document.getElementById("user-input");
const sendBtn = document.getElementById("send-btn");
const micBtn = document.getElementById("mic-btn");
const messages = document.getElementById("messages");
const img = document.getElementById("persona-img");

function appendMessage(from, text) {
  const div = document.createElement("div");
  div.innerHTML = `<b>${from}:</b> ${text}`;
  messages.appendChild(div);
  messages.scrollTop = messages.scrollHeight;
}

sendBtn.onclick = async () => {
  const userText = inputBox.value.trim();
  if (!userText) return;
  appendMessage("You", userText);
  inputBox.value = "";

  const res = await fetch(`${API_BASE_URL}/api/event/dispatch`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ event_type: "text", value: userText })
  });
  const data = await res.json();
  appendMessage("Mia", `Responded to: ${data.value}`);
};

// STT Integration
micBtn.onclick = () => {
  const recognition = new (window.SpeechRecognition || window.webkitSpeechRecognition)();
  recognition.lang = 'en-US';
  recognition.interimResults = false;
  recognition.maxAlternatives = 1;

  recognition.onresult = (event) => {
    const transcript = event.results[0][0].transcript;
    inputBox.value = transcript;
    sendBtn.click();
  };

  recognition.onerror = (event) => {
    console.error("Speech recognition error:", event.error);
  };

  recognition.start();
};
