async function sendMessage() {
  const input = document.getElementById("user-input");
  const message = input.value.trim();
  if (!message) return;

  addMessage(message, "user");
  input.value = "";

  // Show typing animation
  const loadingId = "loading-" + Date.now();
  addMessage("Bot is typing", "bot", loadingId, true);

  try {
    const response = await fetch("/chat", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ message }),
    });

    const data = await response.json();

    // Remove typing animation
    document.getElementById(loadingId).remove();

    // Show bot reply
    addMessage(data.reply, "bot");

  } catch (error) {
    document.getElementById(loadingId).remove();
    addMessage("⚠️ Error contacting server", "bot");
  }
}

function addMessage(message, sender, id = null, typing = false) {
  const chatBox = document.getElementById("chat-box");
  const msgDiv = document.createElement("div");
  msgDiv.classList.add("message", sender);
  if (id) msgDiv.id = id;
  if (typing) msgDiv.classList.add("typing");
  msgDiv.textContent = message;
  chatBox.appendChild(msgDiv);
  chatBox.scrollTop = chatBox.scrollHeight;
}

// Dark Mode Toggle
function toggleDarkMode() {
  document.body.classList.toggle("dark-mode");

  const toggleBtn = document.getElementById("mode-toggle");
  if (document.body.classList.contains("dark-mode")) {
    toggleBtn.textContent = "☀️";
  } else {
    toggleBtn.textContent = "🌙";
  }
}
