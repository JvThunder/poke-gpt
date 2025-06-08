import { useState, useEffect } from 'react';
import './MessageInput.css';

// Updated send icon component with smaller image size
const SendIcon = () => (
    <img
        src="/play-button.png"
        alt="Send"
        style={{ width: '20px', height: '20px' }}
    />
);

function MessageInput({ onSendMessage, isLoading, disabled, message, setMessage }) {
    // Use the message from props if provided, otherwise use local state
    const [localMessage, setLocalMessage] = useState('');

    // Determine if we're using controlled or uncontrolled input
    const isControlled = message !== undefined && setMessage !== undefined;
    const currentMessage = isControlled ? message : localMessage;

    // Function to update the message
    const updateMessage = (newMessage) => {
        if (isControlled) {
            setMessage(newMessage);
        } else {
            setLocalMessage(newMessage);
        }
    };

    // Handle the submit event
    const handleSubmit = (e) => {
        e.preventDefault();
        if (currentMessage.trim() && !isLoading && !disabled) {
            onSendMessage(currentMessage);
            // Only clear the message if using local state
            if (!isControlled) {
                setLocalMessage('');
            }
        }
    };

    const isDisabled = isLoading || disabled;

    return (
        <form className="message-input-container" onSubmit={handleSubmit}>
            <input
                type="text"
                className="message-input"
                placeholder={disabled ? "Chat session unavailable..." : "Ask about Pokémon..."}
                value={currentMessage}
                onChange={(e) => updateMessage(e.target.value)}
                disabled={isDisabled}
            />
            <button
                type="submit"
                className="send-button"
                disabled={isDisabled || !currentMessage.trim()}
            >
                <SendIcon />
            </button>
        </form>
    );
}

export default MessageInput; 