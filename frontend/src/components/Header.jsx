import React from 'react';
import './Header.css';

function Header({ onNewChat, activeTab, onTabChange, favoritesCount }) {
    return (
        <header className="header">
            <div className="container header-container">
                <div className="header-left">
                    <h1 className="header-title">PokéGPT</h1>
                    <div className="header-tabs">
                        <button
                            className={`header-tab ${activeTab === 'chat' ? 'active' : ''}`}
                            onClick={() => onTabChange('chat')}
                        >
                            Chat
                        </button>
                        <button
                            className={`header-tab ${activeTab === 'favorites' ? 'active' : ''}`}
                            onClick={() => onTabChange('favorites')}
                        >
                            Favorites
                            {favoritesCount > 0 && (
                                <span className="favorites-badge" title={`${favoritesCount} Pokémon in favorites`}>
                                    {favoritesCount}
                                </span>
                            )}
                        </button>
                    </div>
                </div>
                <button className="new-chat-btn" onClick={onNewChat}>
                    New Chat
                </button>
            </div>
        </header>
    );
}

export default Header;