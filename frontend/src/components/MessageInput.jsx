import { useState } from 'react';
import './MessageInput.css';

// Updated send icon component with smaller image size
const SendIcon = () => (
    <img
        src="/play-button.png"
        alt="Send"
        style={{ width: '20px', height: '20px' }}
    />
);

function MessageInput({ onSendMessage, isLoading, disabled }) {
    const [message, setMessage] = useState('');

    const handleSubmit = (e) => {
        e.preventDefault();
        if (message.trim() && !isLoading && !disabled) {
            onSendMessage(message);
            setMessage('');
        }
    };

    const isDisabled = isLoading || disabled;

    return (
        <form className="message-input-container" onSubmit={handleSubmit}>
            <input
                type="text"
                className="message-input"
                placeholder={disabled ? "Chat session unavailable..." : "Ask about Pokémon..."}
                value={message}
                onChange={(e) => setMessage(e.target.value)}
                disabled={isDisabled}
            />
            <button
                type="submit"
                className="send-button"
                disabled={isDisabled || !message.trim()}
            >
                <SendIcon />
            </button>
        </form>
    );
}

export default MessageInput; 