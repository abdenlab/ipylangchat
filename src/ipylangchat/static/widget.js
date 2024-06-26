/**
 * A message in the chat.
 *
 * @class Message
 * @property {HTMLDivElement} el - The message element.
 * @property {HTMLSpanElement} sender - The sender element.
 * @property {HTMLSpanElement} content - The content element.
 * @property {number} thinking - Interval id for the thinking animation.
 * @notes Messages authored by "Assistant" will start with a thinking animation.
 *
 * @param {string} sender - The author of the message, e.g. "User", "Assistant".
 * @param {string} content - The text of the message. {optional}
 * @returns {Message}
 */
class Message {
  el = document.createElement("div");
  sender = document.createElement("span");
  content = document.createElement("span");
  thinking = null;

  constructor(sender, content = "") {
    this.el.className = "message";
    this.el.appendChild(this.sender);
    this.sender.className = "message-sender";
    this.el.appendChild(this.content);
    this.content.className = "message-content";

    if (sender === "Assistant") {
      setTimeout(() => {
        this.sender.innerHTML = `<strong>${sender}:</strong> `;
        let i = 0;
        let think = () => {
          this.content.innerText = ".".repeat(i % 4);
          i += 1;
        };
        this.thinking = setInterval(think, 500);
      }, 500);
    } else {
      this.sender.innerHTML = `<strong>${sender}:</strong> `;
      if (content) {
        this.content.innerText = content;
      }
    }
  }

  /**
   * Append text to the message (for streaming output).
   *
   * @param {string} text - The text to append.
   */
  appendText(text) {
    if (this.thinking) {
      clearInterval(this.thinking);
      this.thinking = null;
      this.content.innerText = "";
    }
    this.content.innerText += text;
  }
}

/** @typedef {{ user_msg: String, ai_msg: String }} Model */

/** @type {import("npm:@anywidget/types").Render<Model>} */
function render({ model, el }) {
  let chatContainer = document.createElement("div");
  chatContainer.classList.add("chat-container");
  el.appendChild(chatContainer);

  let chatBox = document.createElement("div");
  chatBox.classList.add("chat-box");
  chatBox.id = "chat-box";
  chatContainer.appendChild(chatBox);

  let inputContainer = document.createElement("div");
  inputContainer.classList.add("input-container");
  chatContainer.appendChild(inputContainer);

  let chatInput = document.createElement("input");
  chatInput.type = "text";
  chatInput.id = "chat-input";
  chatInput.placeholder = "Type your message...";
  inputContainer.appendChild(chatInput);

  let sendButton = document.createElement("button");
  sendButton.id = "send-btn";
  sendButton.textContent = "Send";
  inputContainer.appendChild(sendButton);

  function sendUserMessage() {
    const messageText = chatInput.value.trim();
    if (messageText) {
      const message = new Message("User", messageText);
      chatBox.appendChild(message.el);
      chatBox.scrollTop = chatBox.scrollHeight;
      model.set("user_msg", messageText);
      model.save_changes();
      chatInput.value = "";
    }
  }
  sendButton.addEventListener("click", () => sendUserMessage());
  chatInput.addEventListener("keypress", (event) => {
    if (event.key === "Enter") {
      sendUserMessage();
    }
  });

  let current = null;
  model.on("msg:custom", (msg) => {
    if (msg.type == "create") {
      current = new Message("Assistant");
      chatBox.appendChild(current.el);
      chatBox.scrollTop = chatBox.scrollHeight;
    }
    if (msg.type == "append") {
      current.appendText(msg.text);
    }
    if (msg.type == "finish") {
      model.set("ai_msg", current.content.innerText);
      model.save_changes();
      current = null;
    }
  });
}

export default { render };
