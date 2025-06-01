import React from 'react';
import './Header.css';

function Header({ onNewChat }) {
    return (
        <header className="header">
            <div className="container header-container">
                <h1 className="header-title">PokéGPT</h1>
                <button className="new-chat-btn" onClick={onNewChat}>
                    New Chat
                </button>
            </div>
        </header>
    );
}

export default Header; 