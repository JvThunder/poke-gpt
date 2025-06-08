import React, { useState, useEffect, useRef } from 'react';
import api from '../api/axios';
import './ChatInterface.css';
import MessageList from './MessageList.jsx';
import MessageInput from './MessageInput.jsx';
import Cookies from 'js-cookie';

function ChatInterface({ chatId, refreshFavorites, userId }) {
    const [messages, setMessages] = useState([]);
    const [isLoading, setIsLoading] = useState(false);
    const [error, setError] = useState(null);
    const [invalidChatId, setInvalidChatId] = useState(false);
    const [chatOwner, setChatOwner] = useState(null);
    const [isOwner, setIsOwner] = useState(false);
    const [inputMessage, setInputMessage] = useState('');
    const messagesEndRef = useRef(null);

    // Get user ID from cookies on mount
    useEffect(() => {
        const userIdFromCookie = Cookies.get('user_id');
        if (userIdFromCookie) {
            console.log('User ID from cookie:', userIdFromCookie);
        }
    }, []);

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
        setInvalidChatId(false);

        try {
            const response = await api.getChatHistory(chatId);
            setMessages(response.data.history);

            // Update ownership information
            setChatOwner(response.data.owner_id);
            setIsOwner(response.data.is_owner);
        } catch (err) {
            console.error('Error loading chat history:', err);

            // Check if the error is due to an invalid chat ID
            if (err.response && err.response.status === 404) {
                setInvalidChatId(true);
                setError('This chat session does not exist. Please create a new chat.');

                // Remove the invalid chatId from URL
                const url = new URL(window.location);
                url.searchParams.delete('chatId');
                window.history.pushState({}, '', url);

                // Redirect to home after a short delay
                setTimeout(() => {
                    window.location.reload();
                }, 3000);
            } else {
                setError('Failed to load chat history. Please try again.');
            }
        } finally {
            setIsLoading(false);
        }
    };

    // Check if an AI message contains favorites-related actions
    const checkForFavoriteAction = (content) => {
        if (!content) return false;

        // Check if the message mentions adding to favorites
        const addedToFavorites = content.includes("added to your favorites") ||
            content.includes("added to favorites") ||
            content.includes("Successfully added");

        // Check if the message mentions removing from favorites
        const removedFromFavorites = content.includes("removed from your favorites") ||
            content.includes("removed from favorites");

        return addedToFavorites || removedFromFavorites;
    };

    // Handle example click to autofill the input
    const handleExampleClick = (exampleText) => {
        setInputMessage(exampleText);
    };

    // Send a message to the API
    const handleSendMessage = async (userInput) => {
        if (!userInput.trim()) return;

        const newMessages = [...messages, { role: 'user', content: userInput }];
        setMessages(newMessages);
        setIsLoading(true);
        setInputMessage('');

        try {
            // Use the new api.sendMessage function
            const response = await api.sendMessage(userInput, chatId);

            // The response from the API now includes 'response' and 'tool_calls'
            const assistantMessage = {
                role: 'assistant',
                content: response.data.response, // The text response
                tool_calls: response.data.tool_calls || [] // The tool calls
            };
            setMessages([...newMessages, assistantMessage]);

            // Check if this message is about favorites and refresh if needed
            if (checkForFavoriteAction(assistantMessage.content)) {
                if (refreshFavorites) {
                    refreshFavorites();
                }
            }
        } catch (error) {
            console.error("Failed to send message:", error);
            const errorMessage = {
                role: 'assistant',
                content: "Sorry, I couldn't get a response. Please try again.",
                isError: true
            };
            setMessages([...newMessages, errorMessage]);
        } finally {
            setIsLoading(false);
        }
    };

    return (
        <div className="chat-interface">
            {error && <div className="chat-error">{error}</div>}

            <MessageList
                messages={messages}
                isLoading={isLoading}
                onExampleClick={handleExampleClick}
            />
            <div ref={messagesEndRef} />

            <MessageInput
                onSendMessage={handleSendMessage}
                isLoading={isLoading}
                disabled={invalidChatId}
                message={inputMessage}
                setMessage={setInputMessage}
            />

            <div className="chat-info">
                {userId && (
                    <div className="user-id-display">
                        Your ID: {userId.substring(0, 8)}...
                    </div>
                )}
                {chatOwner && (
                    <div className={`chat-owner ${isOwner ? 'is-owner' : ''}`}>
                        {isOwner ? 'You own this chat' : `Chat owner: ${chatOwner.substring(0, 8)}...`}
                    </div>
                )}
            </div>
        </div>
    );
}

export default ChatInterface; 