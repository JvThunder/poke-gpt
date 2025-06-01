import React from 'react';
import ReactMarkdown from 'react-markdown';
import remarkGfm from 'remark-gfm';
import './MessageList.css';

function MessageList({ messages, isLoading }) {
    return (
        <div className="message-list">
            {messages.length === 0 ? (
                <div className="empty-chat">
                    <h3>Welcome to PokéGPT!</h3>
                    <p>Ask any question about Pokémon to get started.</p>
                    <p className="examples">
                        <strong>Examples:</strong>
                        <ul>
                            <li>What are the abilities of Pikachu?</li>
                            <li>Tell me about the Stench ability</li>
                            <li>List the first 5 Pokémon</li>
                            <li>What type is Charizard?</li>
                        </ul>
                    </p>
                </div>
            ) : (
                messages.map((message, index) => (
                    <div
                        key={index}
                        className={`message ${message.role === 'user' ? 'user-message' : 'assistant-message'}`}
                    >
                        <div className="message-bubble">
                            {message.role === 'assistant' ? (
                                <ReactMarkdown remarkPlugins={[remarkGfm]}>
                                    {message.content}
                                </ReactMarkdown>
                            ) : (
                                message.content
                            )}
                        </div>
                    </div>
                ))
            )}

            {isLoading && (
                <div className="message assistant-message">
                    <div className="message-bubble loading-bubble">
                        <div className="loading-indicator">
                            <div className="dot"></div>
                            <div className="dot"></div>
                            <div className="dot"></div>
                        </div>
                    </div>
                </div>
            )}
        </div>
    );
}

export default MessageList; 