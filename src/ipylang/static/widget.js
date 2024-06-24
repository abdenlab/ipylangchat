/** @typedef {{ value: number }} Model */

/** @type {import("npm:@anywidget/types").Render<Model>} */
function render({ model, el }) {
    let chatContainer = document.createElement('div');
    chatContainer.classList.add('chat-container');
    el.appendChild(chatContainer);
    
    let chatBox = document.createElement('div');
    chatBox.classList.add('chat-box');
    chatBox.id = 'chat-box';
    chatContainer.appendChild(chatBox);
    
    let inputContainer = document.createElement('div');
    inputContainer.classList.add('input-container');
    chatContainer.appendChild(inputContainer);
    
    let chatInput = document.createElement('input');
    chatInput.type = 'text';
    chatInput.id = 'chat-input';
    chatInput.placeholder = 'Type your message...';
    inputContainer.appendChild(chatInput);
    
    let sendButton = document.createElement('button');
    sendButton.id = 'send-btn';
    sendButton.textContent = 'Send';
    inputContainer.appendChild(sendButton);
    
    function sendMessage() {
        const message = chatInput.value.trim();
        if (message) {
            appendMessage('User', message);
            model.set("human_msg", message);
            model.save_changes();
            chatInput.value = '';
        }
    }

    function appendMessage(sender, message) {
        const messageElement = document.createElement('div');
        messageElement.classList.add('message');
        messageElement.innerHTML = `<strong>${sender}:</strong> ${message}`;
        chatBox.appendChild(messageElement);
        chatBox.scrollTop = chatBox.scrollHeight;
    }

    sendButton.addEventListener('click', () => sendMessage());
    chatInput.addEventListener('keypress', (event) => {
        if (event.key === 'Enter') {
            sendMessage();
        }
    });
    function on_ai_answer() {
        let ai_message = model.get("ai_msg");
        appendMessage('Assistant', ai_message);
    }
    model.on("change:ai_msg", on_ai_answer);
}

export default { render };
