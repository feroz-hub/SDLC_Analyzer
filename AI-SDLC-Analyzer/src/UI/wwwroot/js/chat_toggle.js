// JavaScript remains unchanged from the original
document.addEventListener('DOMContentLoaded', function() {
    document.querySelector('.container').style.opacity = '0';
    setTimeout(() => {
        document.querySelector('.container').style.opacity = '1';
        document.querySelector('.container').style.transition = 'opacity 0.8s ease';
    }, 100);

    document.getElementById("user-input").addEventListener("keypress", function(event) {
        if (event.key === "Enter") {
            event.preventDefault();
            sendMessage();
        }
    });

    document.getElementById("user-input").focus();
});

function typeText(element, text, minDelay = 5, maxDelay = 15) {
    return new Promise(resolve => {
        let index = 0;
        function type() {
            if (index < text.length) {
                element.innerHTML = `<span>${text.substring(0, index + 1)}</span>`;
                index++;
                const randomDelay = Math.floor(Math.random() * (maxDelay - minDelay + 1) + minDelay);
                setTimeout(type, randomDelay);
            } else {
                resolve();
            }
            document.getElementById("chat-box").scrollTop = document.getElementById("chat-box").scrollHeight;
        }
        type();
    });
}

function expandInput() {
    let inputField = document.getElementById("user-input");
    inputField.style.height = "auto";
    inputField.style.height = (inputField.scrollHeight) + "px";
}

function clearChat() {
    const chatBox = document.getElementById("chat-box");
    const messages = chatBox.querySelectorAll('.message');
    messages.forEach((msg, index) => {
        setTimeout(() => {
            msg.style.opacity = '0';
            msg.style.transform = 'scale(0.8)';
            msg.style.transition = 'all 0.3s ease';
        }, index * 50);
    });

    setTimeout(() => {
        chatBox.innerHTML = '';
        let welcomeMsg = document.createElement("div");
        welcomeMsg.classList.add("message", "bot");
        welcomeMsg.innerHTML = `<span>Hi! How can I help you with SDLC requirements today? 😊</span>`;
        welcomeMsg.style.opacity = '0';
        chatBox.appendChild(welcomeMsg);
        setTimeout(() => {
            welcomeMsg.style.opacity = '1';
            welcomeMsg.style.transition = 'opacity 0.5s ease';
        }, 100);
    }, messages.length * 50 + 300);
}

function showWarning(message) {
    let chatBox = document.getElementById("chat-box");
    let existingWarning = document.querySelector(".message.bot.warning");
    if (existingWarning) {
        existingWarning.remove();
    }

    let warningMessage = document.createElement("div");
    warningMessage.classList.add("message", "bot", "warning");
    warningMessage.innerHTML = `<span style="color: #d32f2f;">⚠️ ${message}</span>`;
    warningMessage.style.opacity = '0';
    chatBox.appendChild(warningMessage);

    setTimeout(() => {
        warningMessage.style.opacity = '1';
        warningMessage.style.transition = 'opacity 0.3s ease';
    }, 50);

    chatBox.scrollTop = chatBox.scrollHeight;
}

async function sendMessage() {
    let userInput = document.getElementById("user-input").value.trim();
    if (!userInput) return;

    let chatBox = document.getElementById("chat-box");
    let inputField = document.getElementById("user-input");
    let sendButton = document.querySelector(".chat-input button");

    if (userInput.split(" ").length === 1) {
        showWarning("Please refine your query for better results. Try adding more context or specific details.");
        return;
    }

    inputField.disabled = true;
    sendButton.disabled = true;
    sendButton.style.opacity = '0.7';

    let userMessage = document.createElement("div");
    userMessage.classList.add("message", "user");
    userMessage.innerHTML = `<span>${userInput}</span>`;
    userMessage.style.opacity = '0';
    chatBox.appendChild(userMessage);

    setTimeout(() => {
        userMessage.style.opacity = '1';
        userMessage.style.transition = 'all 0.3s ease';
    }, 50);

    chatBox.scrollTop = chatBox.scrollHeight;

    let retrievingMessage = document.createElement("div");
    retrievingMessage.classList.add("message", "bot", "retrieving");
    retrievingMessage.innerHTML = `<span>⏳ Searching for relevant SDLC requirements...</span>`;
    retrievingMessage.style.opacity = '0';
    chatBox.appendChild(retrievingMessage);

    setTimeout(() => {
        retrievingMessage.style.opacity = '1';
        retrievingMessage.style.transition = 'opacity 0.3s ease';
    }, 50);

    chatBox.scrollTop = chatBox.scrollHeight;

    let typingIndicator = document.createElement("div");
    typingIndicator.classList.add("message", "bot", "typing-indicator");
    typingIndicator.innerHTML = `<span>🤖 Analyzing<span class="dots-animation"></span></span>`;
    typingIndicator.style.opacity = '0';
    chatBox.appendChild(typingIndicator);

    setTimeout(() => {
        typingIndicator.style.opacity = '1';
        typingIndicator.style.transition = 'opacity 0.3s ease';
    }, 50);

    chatBox.scrollTop = chatBox.scrollHeight;

    try {
        const selectedModel = document.getElementById("model-select").value;
        const selectedMethod = document.getElementById("method-select").value;

        let response = await fetch("/Requirement/ChatQuery", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({
                query: userInput,
                model: selectedModel,
                method: selectedMethod
            })
        });

        let data = await response.json();

        retrievingMessage.style.opacity = '0';
        setTimeout(() => {
            chatBox.removeChild(retrievingMessage);
        }, 300);

        typingIndicator.style.opacity = '0';
        setTimeout(() => {
            chatBox.removeChild(typingIndicator);
        }, 300);

        if (data.error) {
            let errorMessage = document.createElement("div");
            errorMessage.classList.add("message", "bot", "warning");
            errorMessage.innerHTML = `<span>⚠️ ${data.error}</span>`;
            errorMessage.style.opacity = '0';
            chatBox.appendChild(errorMessage);

            setTimeout(() => {
                errorMessage.style.opacity = '1';
                errorMessage.style.transition = 'opacity 0.3s ease';
            }, 50);
        } else {
            if (data.length === 0) {
                let noResultsMessage = document.createElement("div");
                noResultsMessage.classList.add("message", "bot");
                noResultsMessage.innerHTML = `<span>I couldn't find any specific requirements matching your query. Could you please provide more details or try different keywords?</span>`;
                noResultsMessage.style.opacity = '0';
                chatBox.appendChild(noResultsMessage);

                setTimeout(() => {
                    noResultsMessage.style.opacity = '1';
                    noResultsMessage.style.transition = 'opacity 0.3s ease';
                }, 50);
            } else {
                for (let i = 0; i < data.length; i++) {
                    const req = data[i];

                    if (i > 0) {
                        await new Promise(res => setTimeout(res, 800));
                    }

                    let responseMessage = document.createElement("div");
                    responseMessage.classList.add("message", "bot");
                    responseMessage.innerHTML = `
                        <div class="requirement-header">
                            <strong>📌 ${req.requirementDescription}</strong>
                        </div>
                        <div class="requirement-category">
                            <strong>Category:</strong> ${req.category}
                        </div>
                    `;
                    responseMessage.style.opacity = '0';
                    chatBox.appendChild(responseMessage);

                    setTimeout(() => {
                        responseMessage.style.opacity = '1';
                        responseMessage.style.transition = 'all 0.5s ease';
                    }, 50);

                    chatBox.scrollTop = chatBox.scrollHeight;

                    await new Promise(res => setTimeout(res, 600));

                    for (let j = 0; j < req.changeInRequirement.length; j++) {
                        const change = req.changeInRequirement[j];

                        let changeTyping = document.createElement("div");
                        changeTyping.classList.add("message", "bot", "typing-indicator");
                        changeTyping.innerHTML = `<span>🤖 Adding details<span class="dots-animation"></span></span>`;
                        changeTyping.style.opacity = '0';
                        chatBox.appendChild(changeTyping);

                        setTimeout(() => {
                            changeTyping.style.opacity = '1';
                            changeTyping.style.transition = 'opacity 0.3s ease';
                        }, 50);

                        chatBox.scrollTop = chatBox.scrollHeight;

                        await new Promise(res => setTimeout(res, 700));

                        changeTyping.style.opacity = '0';
                        setTimeout(() => {
                            chatBox.removeChild(changeTyping);
                        }, 300);

                        let changeMessage = document.createElement("div");
                        changeMessage.classList.add("message", "bot", "change-item");
                        chatBox.appendChild(changeMessage);

                        let messageContent = `🔹 ${change}`;
                        await typeText(changeMessage, messageContent, 5, 15);

                        await new Promise(res => setTimeout(res, 300));
                    }
                }
            }
        }
    } catch (error) {
        chatBox.removeChild(retrievingMessage);
        chatBox.removeChild(typingIndicator);

        let errorMessage = document.createElement("div");
        errorMessage.classList.add("message", "bot", "warning");
        errorMessage.innerHTML = `<span>⚠️ Something went wrong. Please try again later.</span>`;
        errorMessage.style.opacity = '0';
        chatBox.appendChild(errorMessage);

        setTimeout(() => {
            errorMessage.style.opacity = '1';
            errorMessage.style.transition = 'opacity 0.3s ease';
        }, 50);

        console.error("Error in chat:", error);
    } finally {
        inputField.value = "";
        inputField.style.height = "auto";

        setTimeout(() => {
            inputField.disabled = false;
            sendButton.disabled = false;
            sendButton.style.opacity = '1';
            sendButton.style.transition = 'opacity 0.3s ease';
            inputField.focus();
        }, 500);
    }
}

document.addEventListener('DOMContentLoaded', function() {
    document.getElementById('model-select').addEventListener('change', function() {
        showModelMethodChange();
    });

    document.getElementById('method-select').addEventListener('change', function() {
        showModelMethodChange();
    });
});

function showModelMethodChange() {
    const chatBox = document.getElementById('chat-box');
    const modelName = document.getElementById('model-select').options[document.getElementById('model-select').selectedIndex].text;
    const methodName = document.getElementById('method-select').options[document.getElementById('method-select').selectedIndex].text;

    let feedbackMsg = document.createElement("div");
    feedbackMsg.classList.add("message", "bot", "system-message");
    feedbackMsg.innerHTML = `<span>ℹ️ Settings updated: Using ${modelName} with ${methodName}</span>`;
    feedbackMsg.style.opacity = '0';
    chatBox.appendChild(feedbackMsg);

    setTimeout(() => {
        feedbackMsg.style.opacity = '1';
        feedbackMsg.style.transition = 'opacity 0.3s ease';
    }, 50);

    chatBox.scrollTop = chatBox.scrollHeight;

    setTimeout(() => {
        feedbackMsg.style.opacity = '0';
        feedbackMsg.style.transition = 'opacity 0.5s ease';
        setTimeout(() => {
            if (feedbackMsg.parentNode === chatBox) {
                chatBox.removeChild(feedbackMsg);
            }
        }, 500);
    }, 3000);
}