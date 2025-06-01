import React, { useState, useEffect } from 'react';
import api from './api/axios';
import './App.css';
import ChatInterface from './components/ChatInterface.jsx';
import Header from './components/Header.jsx';

function App() {
    const [chatId, setChatId] = useState(null);
    const [isLoading, setIsLoading] = useState(false);
    const [error, setError] = useState(null);

    // Create a new chat session when the app loads
    useEffect(() => {
        createNewChat();
    }, []);

    // Function to create a new chat session
    const createNewChat = async () => {
        setIsLoading(true);
        setError(null);
        try {
            const response = await api.post('/create_chat');
            setChatId(response.data.chat_id);
        } catch (err) {
            setError('Failed to create chat session. Please try again.');
            console.error('Error creating chat:', err);
        } finally {
            setIsLoading(false);
        }
    };

    return (
        <div className="app">
            <Header onNewChat={createNewChat} />
            <main className="container">
                {error && <div className="error-message">{error}</div>}
                {isLoading && !chatId ? (
                    <div className="loading">Creating chat session...</div>
                ) : (
                    chatId && <ChatInterface chatId={chatId} />
                )}
            </main>
        </div>
    );
}

export default App; 