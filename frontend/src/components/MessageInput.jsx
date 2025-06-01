import { useState } from 'react';
import './MessageInput.css';

// Simple send icon component
const SendIcon = () => (
    <svg
        width="24"
        height="24"
        viewBox="0 0 24 24"
        fill="none"
        xmlns="http://www.w3.org/2000/svg"
    >
        <path
            d="M3 20V4L22 12L3 20ZM5 17L17 12L5 7V10.5L11 12L5 13.5V17Z"
            fill="currentColor"
        />
    </svg>
);

function MessageInput({ onSendMessage, isLoading }) {
    const [message, setMessage] = useState('');

    const handleSubmit = (e) => {
        e.preventDefault();
        if (message.trim() && !isLoading) {
            onSendMessage(message);
            setMessage('');
        }
    };

    return (
        <form className="message-input-container" onSubmit={handleSubmit}>
            <input
                type="text"
                className="message-input"
                placeholder="Ask about Pokémon..."
                value={message}
                onChange={(e) => setMessage(e.target.value)}
                disabled={isLoading}
            />
            <button
                type="submit"
                className="send-button"
                disabled={isLoading || !message.trim()}
            >
                <SendIcon />
            </button>
        </form>
    );
}

export default MessageInput; 