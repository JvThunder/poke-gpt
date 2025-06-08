import React from 'react';
import ReactMarkdown from 'react-markdown';
import remarkGfm from 'remark-gfm';
import './MessageList.css';
import ToolCall from './ToolCall';

function MessageList({ messages, isLoading, onExampleClick }) {
    // Example questions
    const examples = [
        "What are the abilities of Pikachu?",
        "Tell me about the Stench ability",
        "List the first 5 Pokémon",
        "What type is Charizard?",
        "Add Pikachu to my favorites",
        "Compare my favorite pokemon stats in table format"
    ];

    // Handle example button click
    const handleExampleClick = (example) => {
        if (onExampleClick) {
            onExampleClick(example);
        }
    };

    return (
        <div className="message-list">
            {messages.length === 0 ? (
                <div className="empty-chat">
                    <h3>Welcome to PokéGPT!</h3>
                    <p>Ask any question about Pokémon to get started.</p>
                    <div className="examples">
                        <strong>Examples:</strong>
                        <div className="example-buttons">
                            {examples.map((example, index) => (
                                <button
                                    key={index}
                                    className="example-button"
                                    onClick={() => handleExampleClick(example)}
                                >
                                    {example}
                                </button>
                            ))}
                        </div>
                    </div>
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
                        {message.role === 'assistant' && message.tool_calls && message.tool_calls.length > 0 && (
                            <div className="tool-calls-container">
                                {message.tool_calls.map((toolCall, i) => (
                                    <ToolCall key={i} toolCall={toolCall} />
                                ))}
                            </div>
                        )}
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