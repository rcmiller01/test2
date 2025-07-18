let currentThreadId = null;
let currentMode = "companion";

function createThread() {
  const newThreadId = "thread-" + Date.now();
  const li = document.createElement("li");
  li.textContent = newThreadId;
  li.onclick = () => switchThread(newThreadId);
  document.getElementById("thread-list").appendChild(li);
  switchThread(newThreadId);
}

function switchThread(threadId) {
  currentThreadId = threadId;
  document.getElementById("chat-window").innerHTML = "";
  setContext(threadId, currentMode);
}

function toggleMode() {
  currentMode = document.getElementById("mode-toggle").value;
  if (currentThreadId) {
    setContext(currentThreadId, currentMode);
  }
}

function setContext(threadId, mode) {
  fetch("/api/context/set", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ thread_id: threadId, mode: mode })
  });
}

function sendMessage() {
  const input = document.getElementById("message-input");
  const text = input.value.trim();
  if (!text || !currentThreadId) return;

  appendMessage("You", text);
  input.value = "";

  fetch("/api/event/dispatch", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ event_type: "text", value: text, thread_id: currentThreadId })
  })
  .then(res => res.json())
  .then(data => {
    appendMessage("Response", data.value || "(no reply)");
  });
}

function appendMessage(sender, text) {
  const chatWindow = document.getElementById("chat-window");
  const div = document.createElement("div");
  div.innerHTML = `<b>${sender}:</b> ${text}`;
  chatWindow.appendChild(div);
  chatWindow.scrollTop = chatWindow.scrollHeight;
}
