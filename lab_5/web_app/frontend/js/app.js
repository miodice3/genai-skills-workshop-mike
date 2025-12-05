// API Configuration
const API_BASE_URL = 'http://localhost:8000';

// DOM Elements
const messagesContainer = document.getElementById('messages');
const userInput = document.getElementById('userInput');
const sendButton = document.getElementById('sendButton');
const loadingIndicator = document.getElementById('loading');

// Event Listeners
sendButton.addEventListener('click', handleSendMessage);
userInput.addEventListener('keypress', (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
        e.preventDefault();
        handleSendMessage();
    }
});

/**
 * Handle sending a message to the agent
 */
async function handleSendMessage() {
    const message = userInput.value.trim();

    if (!message) {
        return;
    }

    // Disable input while processing
    setInputState(false);

    // Display user message
    displayMessage(message, 'user');

    // Clear input
    userInput.value = '';

    // Show loading indicator
    showLoading();

    try {
        // Send message to API
        const response = await sendMessageToAPI(message);

        // Hide loading indicator
        hideLoading();

        // Display response
        if (response.blocked) {
            displayBlockedMessage(response.blocked_reason);
        } else {
            displayMessage(response.response, 'assistant');
        }
    } catch (error) {
        // Hide loading indicator
        hideLoading();

        // Display error message
        displayErrorMessage(error.message);
    } finally {
        // Re-enable input
        setInputState(true);
        userInput.focus();
    }
}

/**
 * Send message to the backend API
 * @param {string} message - User's message
 * @returns {Promise<Object>} API response
 */
async function sendMessageToAPI(message) {
    const response = await fetch(`${API_BASE_URL}/api/chat`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({ message }),
    });

    if (!response.ok) {
        const errorData = await response.json().catch(() => ({}));
        throw new Error(
            errorData.detail || `HTTP error! status: ${response.status}`
        );
    }

    return await response.json();
}

/**
 * Display a message in the chat
 * @param {string} text - Message text
 * @param {string} type - Message type: 'user' or 'assistant'
 */
function displayMessage(text, type) {
    const messageDiv = document.createElement('div');
    messageDiv.className = `message ${type}-message`;

    const contentDiv = document.createElement('div');
    contentDiv.className = 'message-content';
    contentDiv.textContent = text;

    messageDiv.appendChild(contentDiv);
    messagesContainer.appendChild(messageDiv);

    scrollToBottom();
}

/**
 * Display a blocked message warning
 * @param {string} reason - Reason for blocking
 */
function displayBlockedMessage(reason) {
    const messageDiv = document.createElement('div');
    messageDiv.className = 'message blocked-message';

    const contentDiv = document.createElement('div');
    contentDiv.className = 'message-content';
    contentDiv.innerHTML = `
        <strong>Content Blocked</strong><br>
        ${reason || 'Your request was blocked for safety reasons.'}
    `;

    messageDiv.appendChild(contentDiv);
    messagesContainer.appendChild(messageDiv);

    scrollToBottom();
}

/**
 * Display an error message
 * @param {string} errorText - Error message
 */
function displayErrorMessage(errorText) {
    const messageDiv = document.createElement('div');
    messageDiv.className = 'message error-message';

    const contentDiv = document.createElement('div');
    contentDiv.className = 'message-content';
    contentDiv.innerHTML = `
        <strong>Error</strong><br>
        ${errorText}<br>
        <small>Please try again or check if the backend is running.</small>
    `;

    messageDiv.appendChild(contentDiv);
    messagesContainer.appendChild(messageDiv);

    scrollToBottom();
}

/**
 * Show loading indicator
 */
function showLoading() {
    loadingIndicator.classList.remove('hidden');
}

/**
 * Hide loading indicator
 */
function hideLoading() {
    loadingIndicator.classList.add('hidden');
}

/**
 * Enable or disable input controls
 * @param {boolean} enabled - Whether to enable the controls
 */
function setInputState(enabled) {
    userInput.disabled = !enabled;
    sendButton.disabled = !enabled;
}

/**
 * Scroll to the bottom of the messages container
 */
function scrollToBottom() {
    messagesContainer.scrollTop = messagesContainer.scrollHeight;
}

// Initialize
document.addEventListener('DOMContentLoaded', () => {
    userInput.focus();
    console.log('Lab 5 Agent Chat initialized');
    console.log(`API Base URL: ${API_BASE_URL}`);
});
