import React, { useState, useEffect, useRef } from 'react';
import api from '../api/axios';
import './ChatInterface.css';
import MessageList from './MessageList.jsx';
import MessageInput from './MessageInput.jsx';

function ChatInterface({ chatId }) {
    const [messages, setMessages] = useState([]);
    const [isLoading, setIsLoading] = useState(false);
    const [error, setError] = useState(null);
    const messagesEndRef = useRef(null);

    // Load chat history when component mounts or chatId changes
    useEffect(() => {
        if (chatId) {
            loadChatHistory();
        }
    }, [chatId]);

    // Scroll to bottom whenever messages change
    useEffect(() => {
        scrollToBottom();
    }, [messages]);

    const scrollToBottom = () => {
        messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
    };

    // Load chat history from the API
    const loadChatHistory = async () => {
        setIsLoading(true);
        setError(null);
        try {
            const response = await api.get(`/chat_history/${chatId}`);
            setMessages(response.data.history);
        } catch (err) {
            setError('Failed to load chat history. Please try again.');
            console.error('Error loading chat history:', err);
        } finally {
            setIsLoading(false);
        }
    };

    // Send a message to the API
    const sendMessage = async (text) => {
        if (!text.trim()) return;

        // Optimistically add user message to UI
        const userMessage = { role: 'user', content: text };
        setMessages([...messages, userMessage]);

        setIsLoading(true);
        setError(null);

        try {
            // Send message to API
            const response = await api.post('/query', {
                query: text,
                chat_id: chatId
            });

            // Add AI response to messages
            const aiMessage = { role: 'assistant', content: response.data.response };
            setMessages(prevMessages => [...prevMessages, aiMessage]);
        } catch (err) {
            setError('Failed to send message. Please try again.');
            console.error('Error sending message:', err);
        } finally {
            setIsLoading(false);
        }
    };

    return (
        <div className="chat-interface">
            {error && <div className="chat-error">{error}</div>}

            <MessageList messages={messages} isLoading={isLoading} />
            <div ref={messagesEndRef} />

            <MessageInput
                onSendMessage={sendMessage}
                isLoading={isLoading}
            />
        </div>
    );
}

export default ChatInterface; 