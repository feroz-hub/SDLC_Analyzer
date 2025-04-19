// Improved animation and interaction functions
document.addEventListener('DOMContentLoaded', function() {
    // Apply initial animations to elements
    document.querySelector('.container').style.opacity = '0';
    setTimeout(() => {
        document.querySelector('.container').style.opacity = '1';
        document.querySelector('.container').style.transition = 'opacity 0.8s ease';
    }, 100);

    // Add event listener for enter key on input
    document.getElementById("user-input").addEventListener("keypress", function(event) {
        if (event.key === "Enter") {
            event.preventDefault();
            sendMessage();
        }
    });

    // Focus input field on page load
    document.getElementById("user-input").focus();

    // Add hover effects to messages
    const addMessageHoverEffects = () => {
        document.querySelectorAll('.message').forEach(msg => {
            msg.addEventListener('mouseenter', () => {
                msg.style.transform = 'translateY(-3px)';
                msg.style.boxShadow = '0 5px 15px rgba(0,0,0,0.1)';
            });
            msg.addEventListener('mouseleave', () => {
                msg.style.transform = 'translateY(0)';
                msg.style.boxShadow = '0 2px 8px rgba(0, 0, 0, 0.07)';
            });
        });
    };

    // Initialize hover effects
    addMessageHoverEffects();

    // Add change listeners to dropdowns
    document.getElementById('model-select').addEventListener('change', function() {
        showModelMethodChange();
    });

    document.getElementById('method-select').addEventListener('change', function() {
        showModelMethodChange();
    });

    // Add subtle parallax effect to chat box on desktop
    if (window.innerWidth > 768) {
        const chatBox = document.getElementById('chat-box');
        document.addEventListener('mousemove', function(e) {
            const x = e.clientX / window.innerWidth;
            const y = e.clientY / window.innerHeight;

            chatBox.style.transform = `perspective(1000px) rotateY(${x * 2 - 1}deg) rotateX(${-y * 2 + 1}deg)`;
            chatBox.style.transition = 'transform 0.1s ease-out';
        });

        // Reset transform when mouse leaves the window
        document.addEventListener('mouseleave', function() {
            chatBox.style.transform = 'perspective(1000px) rotateY(0deg) rotateX(0deg)';
            chatBox.style.transition = 'transform 0.5s ease-out';
        });
    }
});

// Enhanced typing effect with variable speed and animated cursor
function typeText(element, text, minDelay = 5, maxDelay = 15) {
    return new Promise(resolve => {
        let index = 0;

        // Create text container and cursor element
        let textContainer = document.createElement('span');
        let cursor = document.createElement('span');
        cursor.innerHTML = '|';
        cursor.style.marginLeft = '2px';
        cursor.style.animation = 'blink 0.7s infinite';
        cursor.style.opacity = '0.7';

        element.appendChild(textContainer);
        element.appendChild(cursor);

        function type() {
            if (index < text.length) {
                // Add character by character with effects
                textContainer.innerHTML = text.substring(0, index + 1);
                index++;

                // Random delay for more natural typing
                const randomDelay = Math.floor(Math.random() * (maxDelay - minDelay + 1) + minDelay);

                // Add a longer pause at commas and periods
                if (text[index - 1] === ',' || text[index - 1] === '.') {
                    setTimeout(type, randomDelay * 5);
                } else {
                    setTimeout(type, randomDelay);
                }
            } else {
                // Typing finished - remove cursor with fade out
                cursor.style.opacity = '0';
                cursor.style.transition = 'opacity 0.3s ease';
                setTimeout(() => {
                    if (cursor.parentNode === element) {
                        element.removeChild(cursor);
                    }
                    resolve();
                }, 300);
            }

            // Auto-scroll with smooth effect
            const chatBox = document.getElementById("chat-box");
            chatBox.scrollTo({
                top: chatBox.scrollHeight,
                behavior: 'smooth'
            });
        }

        type();
    });
}

// Auto-resizing input field with animation
function expandInput() {
    let inputField = document.getElementById("user-input");
    // Reset height to calculate new height
    inputField.style.height = "auto";
    // Set new height based on content (with limits)
    const newHeight = Math.min(Math.max(inputField.scrollHeight, 50), 150);
    inputField.style.height = newHeight + "px";
    inputField.style.transition = 'height 0.2s ease';
}

// Enhanced clear chat with dynamic animation
function clearChat() {
    const chatBox = document.getElementById("chat-box");

    // Add wave effect
    const wave = document.createElement('div');
    wave.style.position = 'absolute';
    wave.style.top = '0';
    wave.style.left = '0';
    wave.style.right = '0';
    wave.style.bottom = '0';
    wave.style.background = 'radial-gradient(circle at center, rgba(255,255,255,0.8) 0%, rgba(255,255,255,0) 70%)';
    wave.style.borderRadius = 'inherit';
    wave.style.zIndex = '5';
    wave.style.pointerEvents = 'none';
    wave.style.opacity = '0';
    wave.style.transform = 'scale(0)';
    wave.style.transition = 'all 0.6s cubic-bezier(0.22, 1, 0.36, 1)';

    chatBox.appendChild(wave);

    // Trigger wave animation
    setTimeout(() => {
        wave.style.opacity = '1';
        wave.style.transform = 'scale(2)';
    }, 10);

    // Fade out all messages with cascade effect
    const messages = chatBox.querySelectorAll('.message');
    messages.forEach((msg, index) => {
        setTimeout(() => {
            msg.style.opacity = '0';
            msg.style.transform = 'scale(0.8) translateY(20px)';
            msg.style.transition = 'all 0.5s cubic-bezier(0.22, 1, 0.36, 1)';
        }, index * 50);
    });

    // After fade-out animation, clear and add welcome message
    setTimeout(() => {
        chatBox.innerHTML = '';

        // Clean up wave effect
        if (wave.parentNode === chatBox) {
            chatBox.removeChild(wave);
        }

        // Add welcome message with animation
        let welcomeMsg = document.createElement("div");
        welcomeMsg.classList.add("message", "bot");
        welcomeMsg.innerHTML = `<span>Hi! How can I help you with SDLC requirements today? 😊</span>`;
        welcomeMsg.style.opacity = '0';
        welcomeMsg.style.transform = 'scale(0.9)';
        chatBox.appendChild(welcomeMsg);

        setTimeout(() => {
            welcomeMsg.style.opacity = '1';
            welcomeMsg.style.transform = 'scale(1)';
            welcomeMsg.style.transition = 'all 0.5s cubic-bezier(0.22, 1, 0.36, 1)';
            // Re-add hover effects to the new message
            welcomeMsg.addEventListener('mouseenter', () => {
                welcomeMsg.style.transform = 'translateY(-3px)';
                welcomeMsg.style.boxShadow = '0 5px 15px rgba(0,0,0,0.1)';
            });
            welcomeMsg.addEventListener('mouseleave', () => {
                welcomeMsg.style.transform = 'translateY(0)';
                welcomeMsg.style.boxShadow = '0 2px 8px rgba(0, 0, 0, 0.07)';
            });
        }, 100);
    }, messages.length * 50 + 600);
}

// Enhanced animated warning display
function showWarning(message) {
    let chatBox = document.getElementById("chat-box");

    // Remove existing warning with fade out
    let existingWarning = document.querySelector(".message.bot.warning");
    if (existingWarning) {
        existingWarning.style.opacity = '0';
        existingWarning.style.transform = 'translateY(10px)';
        existingWarning.style.transition = 'all 0.3s ease';

        setTimeout(() => {
            if (existingWarning.parentNode === chatBox) {
                chatBox.removeChild(existingWarning);
            }
        }, 300);

        // Short delay before showing new warning
        setTimeout(createWarning, 350);
    } else {
        createWarning();
    }

    function createWarning() {
        // Create new warning with animation
        let warningMessage = document.createElement("div");
        warningMessage.classList.add("message", "bot", "warning");
        warningMessage.innerHTML = `<span>⚠️ ${message}</span>`;
        warningMessage.style.opacity = '0';
        warningMessage.style.transform = 'translateY(-10px)';
        chatBox.appendChild(warningMessage);

        setTimeout(() => {
            warningMessage.style.opacity = '1';
            warningMessage.style.transform = 'translateY(0)';
            warningMessage.style.transition = 'all 0.4s cubic-bezier(0.22, 1, 0.36, 1)';

            // Add hover effects
            warningMessage.addEventListener('mouseenter', () => {
                warningMessage.style.transform = 'translateY(-3px)';
                warningMessage.style.boxShadow = '0 5px 15px rgba(244, 67, 54, 0.2)';
            });
            warningMessage.addEventListener('mouseleave', () => {
                warningMessage.style.transform = 'translateY(0)';
                warningMessage.style.boxShadow = '0 2px 8px rgba(0, 0, 0, 0.07)';
            });
        }, 50);

        // Auto-dismiss warning after a delay
        setTimeout(() => {
            if (warningMessage.parentNode === chatBox) {
                warningMessage.style.opacity = '0';
                warningMessage.style.transform = 'translateY(10px)';
                warningMessage.style.transition = 'all 0.5s ease';

                setTimeout(() => {
                    if (warningMessage.parentNode === chatBox) {
                        chatBox.removeChild(warningMessage);
                    }
                }, 500);
            }
        }, 8000);

        chatBox.scrollTo({
            top: chatBox.scrollHeight,
            behavior: 'smooth'
        });
    }
}

// Show feedback when model or method is changed
function showModelMethodChange() {
    const chatBox = document.getElementById('chat-box');
    const modelName = document.getElementById('model-select').options[document.getElementById('model-select').selectedIndex].text;
    const methodName = document.getElementById('method-select').options[document.getElementById('method-select').selectedIndex].text;

    // Find and remove any existing system messages
    let existingMsg = document.querySelector(".message.bot.system-message");
    if (existingMsg) {
        existingMsg.style.opacity = '0';
        existingMsg.style.transform = 'translateY(10px)';
        existingMsg.style.transition = 'all 0.3s ease';

        setTimeout(() => {
            if (existingMsg.parentNode === chatBox) {
                chatBox.removeChild(existingMsg);
            }
        }, 300);

        // Short delay before showing new message
        setTimeout(createMessage, 350);
    } else {
        createMessage();
    }

    function createMessage() {
        let feedbackMsg = document.createElement("div");
        feedbackMsg.classList.add("message", "bot", "system-message");
        feedbackMsg.innerHTML = `<span>🔄 Settings updated: Using <strong>${modelName}</strong> with <strong>${methodName}</strong></span>`;
        feedbackMsg.style.opacity = '0';
        feedbackMsg.style.transform = 'translateY(-10px)';
        chatBox.appendChild(feedbackMsg);

        setTimeout(() => {
            feedbackMsg.style.opacity = '1';
            feedbackMsg.style.transform = 'translateY(0)';
            feedbackMsg.style.transition = 'all 0.4s cubic-bezier(0.22, 1, 0.36, 1)';
        }, 50);

        chatBox.scrollTo({
            top: chatBox.scrollHeight,
            behavior: 'smooth'
        });

        // Add subtle shimmer effect to show change
        const selects = document.querySelectorAll('select');
        selects.forEach(select => {
            select.style.boxShadow = '0 0 10px rgba(33, 150, 243, 0.5)';
            setTimeout(() => {
                select.style.boxShadow = '';
                select.style.transition = 'box-shadow 0.5s ease';
            }, 800);
        });

        // Auto-remove after a few seconds
        setTimeout(() => {
            feedbackMsg.style.opacity = '0';
            feedbackMsg.style.transform = 'translateY(10px)';
            feedbackMsg.style.transition = 'all 0.5s ease';

            setTimeout(() => {
                if (feedbackMsg.parentNode === chatBox) {
                    chatBox.removeChild(feedbackMsg);
                }
            }, 500);
        }, 4000);
    }
}

// Enhanced send message function with advanced animations
async function sendMessage() {
    let userInput = document.getElementById("user-input").value.trim();
    if (!userInput) return;

    let chatBox = document.getElementById("chat-box");
    let inputField = document.getElementById("user-input");
    let sendButton = document.querySelector(".chat-input button");

    // Validate query length
    if (userInput.split(" ").length === 1) {
        showWarning("Please refine your query for better results. Try adding more context or specific details.");
        // Add shake animation to input field
        inputField.style.animation = 'shake 0.5s cubic-bezier(.36,.07,.19,.97) both';
        setTimeout(() => {
            inputField.style.animation = '';
        }, 500);
        return;
    }

    // Disable inputs during processing
    inputField.disabled = true;
    sendButton.disabled = true;
    sendButton.style.opacity = '0.7';

    // Add send button animation
    sendButton.innerHTML = '<span style="display: inline-block; animation: spin 1s infinite linear;">⏳</span>';

    // Append user message with staggered animation
    let userMessage = document.createElement("div");
    userMessage.classList.add("message", "user");
    userMessage.style.opacity = '0';
    userMessage.style.transform = 'translateY(20px)';
    userMessage.innerHTML = `<span>${userInput}</span>`;
    chatBox.appendChild(userMessage);

    setTimeout(() => {
        userMessage.style.opacity = '1';
        userMessage.style.transform = 'translateY(0)';
        userMessage.style.transition = 'all 0.4s cubic-bezier(0.22, 1, 0.36, 1)';

        // Add hover effects
        userMessage.addEventListener('mouseenter', () => {
            userMessage.style.transform = 'translateY(-3px)';
            userMessage.style.boxShadow = '0 5px 15px rgba(0,0,0,0.1)';
        });
        userMessage.addEventListener('mouseleave', () => {
            userMessage.style.transform = 'translateY(0)';
            userMessage.style.boxShadow = '0 2px 8px rgba(0, 0, 0, 0.07)';
        });
    }, 50);

    chatBox.scrollTo({
        top: chatBox.scrollHeight,
        behavior: 'smooth'
    });

    // Show retrieving message with pulse animation
    let retrievingMessage = document.createElement("div");
    retrievingMessage.classList.add("message", "bot", "retrieving");
    retrievingMessage.innerHTML = `<span>⏳ Searching for relevant SDLC requirements...</span>`;
    retrievingMessage.style.opacity = '0';
    retrievingMessage.style.transform = 'translateY(20px)';
    chatBox.appendChild(retrievingMessage);

    setTimeout(() => {
        retrievingMessage.style.opacity = '1';
        retrievingMessage.style.transform = 'translateY(0)';
        retrievingMessage.style.transition = 'all 0.4s cubic-bezier(0.22, 1, 0.36, 1)';
    }, 400); // Slight delay for better user experience

    chatBox.scrollTo({
        top: chatBox.scrollHeight,
        behavior: 'smooth'
    });

    // Add typing indicator with dots animation
    let typingIndicator = document.createElement("div");
    typingIndicator.classList.add("message", "bot", "typing-indicator");
    typingIndicator.innerHTML = `<span>🤖 Analyzing<span class="dots-animation"></span></span>`;
    typingIndicator.style.opacity = '0';
    typingIndicator.style.transform = 'translateY(20px)';
    chatBox.appendChild(typingIndicator);

    setTimeout(() => {
        typingIndicator.style.opacity = '1';
        typingIndicator.style.transform = 'translateY(0)';
        typingIndicator.style.transition = 'all 0.4s cubic-bezier(0.22, 1, 0.36, 1)';
    }, 800); // Slightly longer delay for sequence effect

    chatBox.scrollTo({
        top: chatBox.scrollHeight,
        behavior: 'smooth'
    });

    try {
        // Get selected model and method
        const selectedModel = document.getElementById("model-select").value;
        const selectedMethod = document.getElementById("method-select").value;

        // Send API request
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

        // Remove retrieving message with fade-out
        retrievingMessage.style.opacity = '0';
        retrievingMessage.style.transform = 'translateY(10px)';
        retrievingMessage.style.transition = 'all 0.4s ease';

        setTimeout(() => {
            if (retrievingMessage.parentNode === chatBox) {
                chatBox.removeChild(retrievingMessage);
            }
        }, 400);

        // Remove typing indicator with fade-out
        typingIndicator.style.opacity = '0';
        typingIndicator.style.transform = 'translateY(10px)';
        typingIndicator.style.transition = 'all 0.4s ease';

        setTimeout(() => {
            if (typingIndicator.parentNode === chatBox) {
                chatBox.removeChild(typingIndicator);
            }
        }, 400);

        if (data.error) {
            // Display error with animation
            let errorMessage = document.createElement("div");
            errorMessage.classList.add("message", "bot", "warning");
            errorMessage.innerHTML = `<span>⚠️ ${data.error}</span>`;
            errorMessage.style.opacity = '0';
            errorMessage.style.transform = 'translateY(20px)';
            chatBox.appendChild(errorMessage);

            setTimeout(() => {
                errorMessage.style.opacity = '1';
                errorMessage.style.transform = 'translateY(0)';
                errorMessage.style.transition = 'all 0.4s cubic-bezier(0.22, 1, 0.36, 1)';

                // Add hover effects
                errorMessage.addEventListener('mouseenter', () => {
                    errorMessage.style.transform = 'translateY(-3px)';
                    errorMessage.style.boxShadow = '0 5px 15px rgba(244, 67, 54, 0.2)';
                });
                errorMessage.addEventListener('mouseleave', () => {
                    errorMessage.style.transform = 'translateY(0)';
                    errorMessage.style.boxShadow = '0 2px 8px rgba(0, 0, 0, 0.07)';
                });
            }, 50);
        } else {
            // Process requirements with sequential animations
            if (!data || data.length === 0) {
                // No results found
                let noResultsMessage = document.createElement("div");
                noResultsMessage.classList.add("message", "bot");
                noResultsMessage.innerHTML = `<span>I couldn't find any specific requirements matching your query. Could you please provide more details or try different keywords?</span>`;
                noResultsMessage.style.opacity = '0';
                noResultsMessage.style.transform = 'translateY(20px)';
                chatBox.appendChild(noResultsMessage);

                setTimeout(() => {
                    noResultsMessage.style.opacity = '1';
                    noResultsMessage.style.transform = 'translateY(0)';
                    noResultsMessage.style.transition = 'all 0.4s cubic-bezier(0.22, 1, 0.36, 1)';

                    // Add hover effects
                    noResultsMessage.addEventListener('mouseenter', () => {
                        noResultsMessage.style.transform = 'translateY(-3px)';
                        noResultsMessage.style.boxShadow = '0 5px 15px rgba(0,0,0,0.1)';
                    });
                    noResultsMessage.addEventListener('mouseleave', () => {
                        noResultsMessage.style.transform = 'translateY(0)';
                        noResultsMessage.style.boxShadow = '0 2px 8px rgba(0, 0, 0, 0.07)';
                    });
                }, 50);
            } else {
                // Process each requirement with staggered animations
                for (let i = 0; i < data.length; i++) {
                    const req = data[i];

                    // Wait between requirements for better readability
                    if (i > 0) {
                        await new Promise(res => setTimeout(res, 800));
                    }

                    // Display requirement with fade in
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
                    responseMessage.style.transform = 'translateY(20px)';
                    chatBox.appendChild(responseMessage);

                    setTimeout(() => {
                        responseMessage.style.opacity = '1';
                        responseMessage.style.transform = 'translateY(0)';
                        responseMessage.style.transition = 'all 0.5s cubic-bezier(0.22, 1, 0.36, 1)';

                        // Add hover effects
                        responseMessage.addEventListener('mouseenter', () => {
                            responseMessage.style.transform = 'translateY(-3px)';
                            responseMessage.style.boxShadow = '0 5px 15px rgba(0,0,0,0.1)';
                        });
                        responseMessage.addEventListener('mouseleave', () => {
                            responseMessage.style.transform = 'translateY(0)';
                            responseMessage.style.boxShadow = '0 2px 8px rgba(0, 0, 0, 0.07)';
                        });
                    }, 50);

                    chatBox.scrollTo({
                        top: chatBox.scrollHeight,
                        behavior: 'smooth'
                    });

                    // Wait before showing changes
                    await new Promise(res => setTimeout(res, 600));

                    // Process changes with typing animation
                    for (let j = 0; j < req.changeInRequirement.length; j++) {
                        const change = req.changeInRequirement[j];

                        // Add typing indicator for this change
                        let changeTyping = document.createElement("div");
                        changeTyping.classList.add("message", "bot", "typing-indicator");
                        changeTyping.innerHTML = `<span>🤖 Adding details<span class="dots-animation"></span></span>`;
                        changeTyping.style.opacity = '0';
                        changeTyping.style.transform = 'translateY(20px)';
                        chatBox.appendChild(changeTyping);

                        setTimeout(() => {
                            changeTyping.style.opacity = '1';
                            changeTyping.style.transform = 'translateY(0)';
                            changeTyping.style.transition = 'all 0.4s cubic-bezier(0.22, 1, 0.36, 1)';
                        }, 50);

                        chatBox.scrollTo({
                            top: chatBox.scrollHeight,
                            behavior: 'smooth'
                        });

                        // Wait for a moment
                        await new Promise(res => setTimeout(res, 700));

                        // Remove typing indicator
                        changeTyping.style.opacity = '0';
                        changeTyping.style.transform = 'translateY(10px)';
                        changeTyping.style.transition = 'all 0.3s ease';

                        setTimeout(() => {
                            if (changeTyping.parentNode === chatBox) {
                                chatBox.removeChild(changeTyping);
                            }
                        }, 300);

                        // Create change message element
                        let changeMessage = document.createElement("div");
                        changeMessage.classList.add("message", "bot", "change-item");
                        changeMessage.style.opacity = '0';
                        chatBox.appendChild(changeMessage);

                        // Reveal change message container
                        setTimeout(() => {
                            changeMessage.style.opacity = '1';
                            changeMessage.style.transition = 'opacity 0.3s ease';
                        }, 50);

                        // Type out the change content
                        let messageContent = `🔹 ${change}`;
                        await typeText(changeMessage, messageContent, 5, 15);

                        // Add hover effects after typing completed
                        changeMessage.addEventListener('mouseenter', () => {
                            changeMessage.style.transform = 'translateY(-3px)';
                            changeMessage.style.boxShadow = '0 5px 15px rgba(0,0,0,0.1)';
                            changeMessage.style.borderLeftColor = 'var(--primary)';
                            changeMessage.style.transition = 'all 0.3s ease';
                        });
                        changeMessage.addEventListener('mouseleave', () => {
                            changeMessage.style.transform = 'translateY(0)';
                            changeMessage.style.boxShadow = '0 2px 8px rgba(0, 0, 0, 0.07)';
                            changeMessage.style.borderLeftColor = 'rgba(33, 150, 243, 0.3)';
                            changeMessage.style.transition = 'all 0.3s ease';
                        });

                        // Short delay before next change
                        await new Promise(res => setTimeout(res, 300));
                    }
                }
            }
        }
    } catch (error) {
        // Handle errors with animation
        if (retrievingMessage.parentNode === chatBox) {
            chatBox.removeChild(retrievingMessage);
        }
        if (typingIndicator.parentNode === chatBox) {
            chatBox.removeChild(typingIndicator);
        }

        let errorMessage = document.createElement("div");
        errorMessage.classList.add("message", "bot", "warning");
        errorMessage.innerHTML = `<span>⚠️ Something went wrong. Please try again later.</span>`;
        errorMessage.style.opacity = '0';
        errorMessage.style.transform = 'translateY(20px)';
        chatBox.appendChild(errorMessage);

        setTimeout(() => {
            errorMessage.style.opacity = '1';
            errorMessage.style.transform = 'translateY(0)';
            errorMessage.style.transition = 'all 0.4s cubic-bezier(0.22, 1, 0.36, 1)';

            // Add hover effects
            errorMessage.addEventListener('mouseenter', () => {
                errorMessage.style.transform = 'translateY(-3px)';
                errorMessage.style.boxShadow = '0 5px 15px rgba(244, 67, 54, 0.2)';
            });
            errorMessage.addEventListener('mouseleave', () => {
                errorMessage.style.transform = 'translateY(0)';
                errorMessage.style.boxShadow = '0 2px 8px rgba(0, 0, 0, 0.07)';
            });
        }, 50);

        console.error("Error in chat:", error);
    } finally {
        // Re-enable input with animation
        inputField.value = "";
        inputField.style.height = "auto";
        sendButton.innerHTML = "Send";

        // Animation for button return to normal
        sendButton.style.transform = 'scale(0.95)';
        setTimeout(() => {
            sendButton.style.transform = 'scale(1)';
            sendButton.style.transition = 'transform 0.3s cubic-bezier(0.22, 1, 0.36, 1)';
        }, 100);

        // Re-enable with slight delay for better UX
        setTimeout(() => {
            inputField.disabled = false;
            sendButton.disabled = false;
            sendButton.style.opacity = '1';
            sendButton.style.transition = 'opacity 0.3s ease';
            inputField.focus();
        }, 500);
    }
}

// Add CSS for additional animations not included in the CSS file
const animationStyle = document.createElement('style');
animationStyle.textContent = `
    @keyframes blink {
        0%, 100% { opacity: 1; }
        50% { opacity: 0; }
    }
    
    @keyframes spin {
        0% { transform: rotate(0deg); }
        100% { transform: rotate(360deg); }
    }
    
    .pulse-animation {
        animation: pulse 0.5s ease;
    }
`;
document.head.appendChild(animationStyle);