// Global session management
let currentSessionId = null;
let hasStartedConversation = false;
let typingMessages = [
  "💭 Thinking about water conservation...",
  "🌊 Finding the best water tips...",
  "💧 Calculating your water savings...",
  "🚽 Checking bathroom water tips...",
  "🍳 Looking up kitchen conservation ideas..."
];

// Initialize the chat
document.addEventListener('DOMContentLoaded', function() {
  // Add welcome message
  setTimeout(() => {
    addMessage("Hi! I'm your water conservation assistant. I can help you save water, calculate usage, and answer all your water-related questions. How can I help you today?", "bot");
  }, 500);
});

async function sendMessage() {
  const input = document.getElementById("user-input");
  const message = input.value.trim();
  if (!message) return;

  // Hide conversation starters after first message
  if (!hasStartedConversation) {
    hideConversationStarters();
    hasStartedConversation = true;
  }

  addMessage(message, "user");
  input.value = "";

  // Show typing animation with random personality message
  const typingMessage = typingMessages[Math.floor(Math.random() * typingMessages.length)];
  const loadingId = "loading-" + Date.now();
  addMessage(typingMessage, "bot", loadingId, true);

  try {
    const response = await fetch("/chat", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        message: message,
        session_id: currentSessionId
      }),
    });

    const data = await response.json();

    // Update session ID
    if (data.session_id) {
      currentSessionId = data.session_id;
    }

    // Remove typing animation
    document.getElementById(loadingId).remove();

    // Show bot reply
    addMessage(data.reply, "bot");

    // Show quick actions after first bot response
    if (!hasStartedConversation) {
      setTimeout(() => {
        showQuickActions();
      }, 1000);
    }

  } catch (error) {
    document.getElementById(loadingId).remove();
    addMessage("🌊 I'm having some trouble connecting right now. Could you try again in a moment?", "bot");
  }
}

function addMessage(message, sender, id = null, typing = false) {
  const chatBox = document.getElementById("chat-box");
  const msgDiv = document.createElement("div");
  msgDiv.classList.add("message", sender);
  if (id) msgDiv.id = id;
  if (typing) msgDiv.classList.add("typing");

  // Handle formatted messages (line breaks, bold text, etc.)
  if (sender === "bot") {
    msgDiv.innerHTML = formatBotMessage(message);
  } else {
    msgDiv.textContent = message;
  }

  chatBox.appendChild(msgDiv);
  chatBox.scrollTop = chatBox.scrollHeight;
}

function formatBotMessage(message) {
  // Convert markdown-like formatting to HTML
  let formatted = message
    .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')  // Bold text
    .replace(/\*(.*?)\*/g, '<em>$1</em>')              // Italic text
    .replace(/(\d+\))/g, '<span class="step-number">$1</span>')  // Step numbers
    .replace(/([🚽🚿🍳🌱💧🧮💭🌊])/g, '<span class="emoji">$1</span>');  // Emojis

  // Handle line breaks
  formatted = formatted.replace(/\n\n/g, '</p><p>').replace(/\n/g, '<br>');
  formatted = '<p>' + formatted + '</p>';

  return formatted;
}

function useStarter(starterText) {
  document.getElementById("user-input").value = starterText;
  sendMessage();
}

function quickAction(topic) {
  const topicMessages = {
    'kitchen': "What are the best ways to save water in the kitchen?",
    'bathroom': "How can I reduce water usage in my bathroom?",
    'garden': "What are some water-saving tips for my garden?",
    'leaks': "How do I detect and fix water leaks in my home?",
    'calculate': "Can you help me calculate my household water usage?"
  };

  const message = topicMessages[topic] || `Tell me about ${topic} water conservation`;
  document.getElementById("user-input").value = message;
  sendMessage();
}

function hideConversationStarters() {
  const starters = document.getElementById("conversation-starters");
  if (starters) {
    starters.style.transition = "opacity 0.3s, max-height 0.3s";
    starters.style.opacity = "0";
    setTimeout(() => {
      starters.style.display = "none";
    }, 300);
  }
}

function showQuickActions() {
  const quickActions = document.getElementById("quick-actions");
  if (quickActions) {
    quickActions.style.display = "flex";
    quickActions.style.animation = "fadeIn 0.5s ease-in";
  }
}

function openCalculator() {
  document.getElementById("calculator-modal").style.display = "flex";
}

function closeCalculator() {
  document.getElementById("calculator-modal").style.display = "none";
  document.getElementById("calc-results").style.display = "none";
}

async function calculateUsage() {
  const data = {
    showers: parseInt(document.getElementById("showers").value) || 2,
    shower_time: parseInt(document.getElementById("shower_time").value) || 10,
    toilet_flushes: parseInt(document.getElementById("toilet_flushes").value) || 6,
    faucet_use: parseInt(document.getElementById("faucet_use").value) || 5,
    laundry: parseInt(document.getElementById("laundry").value) || 1
  };

  try {
    const response = await fetch("/calculate", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        data: data,
        session_id: currentSessionId
      }),
    });

    const result = await response.json();

    if (result.data) {
      displayCalculationResults(result.data, result.suggestion);

      // Also add the AI response to chat
      addMessage(result.reply, "bot");
    } else {
      addMessage(result.reply, "bot");
    }

  } catch (error) {
    addMessage("💧 I had trouble with that calculation. Let's try a different approach!", "bot");
  }
}

function displayCalculationResults(data, suggestion) {
  const resultsDiv = document.getElementById("calc-results");

  resultsDiv.innerHTML = `
    <h4>💧 Your Water Usage Breakdown</h4>
    <div class="usage-breakdown">
      <div class="usage-item">
        <span>🚿 Showers:</span>
        <span>${data.breakdown.showers} L/day</span>
      </div>
      <div class="usage-item">
        <span>🚽 Toilet:</span>
        <span>${data.breakdown.toilet} L/day</span>
      </div>
      <div class="usage-item">
        <span>🚰 Faucet:</span>
        <span>${data.breakdown.faucet} L/day</span>
      </div>
      <div class="usage-item">
        <span>🧺 Laundry:</span>
        <span>${data.breakdown.laundry} L/day</span>
      </div>
      <div class="usage-total">
        <div class="usage-item">
          <span><strong>Daily Total:</strong></span>
          <span><strong>${data.daily} L</strong></span>
        </div>
        <div class="usage-item">
          <span>Monthly:</span>
          <span>${data.monthly} L</span>
        </div>
        <div class="usage-item">
          <span>Yearly:</span>
          <span>${data.yearly} L</span>
        </div>
      </div>
    </div>
    <p style="margin-top: 10px; font-style: italic; color: var(--water-dark);">
      💡 ${suggestion}
    </p>
  `;

  resultsDiv.style.display = "block";
}

async function clearChat() {
  // Clear the session on the backend
  if (currentSessionId) {
    try {
      await fetch("/clear_session", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ session_id: currentSessionId }),
      });
    } catch (error) {
      console.log("Failed to clear session on server");
    }
  }

  // Reset local state
  currentSessionId = null;
  hasStartedConversation = false;

  // Clear chat messages
  document.getElementById("chat-box").innerHTML = "";

  // Show conversation starters again
  const starters = document.getElementById("conversation-starters");
  if (starters) {
    starters.style.display = "block";
    starters.style.opacity = "1";
  }

  // Hide quick actions
  document.getElementById("quick-actions").style.display = "none";

  // Add fresh welcome message
  addMessage("Great! Let's start fresh. What water conservation topic can I help you with today?", "bot");
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

// Handle Enter key in input field
document.addEventListener('DOMContentLoaded', function() {
  const input = document.getElementById("user-input");
  input.addEventListener("keypress", function(event) {
    if (event.key === "Enter") {
      event.preventDefault();
      sendMessage();
    }
  });

  // Close modal when clicking outside
  document.getElementById("calculator-modal").addEventListener("click", function(event) {
    if (event.target === this) {
      closeCalculator();
    }
  });
});

// Add CSS animation
const style = document.createElement('style');
style.textContent = `
  @keyframes fadeIn {
    from { opacity: 0; transform: translateY(10px); }
    to { opacity: 1; transform: translateY(0); }
  }

  .step-number {
    color: var(--water-blue);
    font-weight: bold;
    margin-right: 5px;
  }

  .emoji {
    font-size: 1.1em;
    margin: 0 2px;
  }
`;
document.head.appendChild(style);
