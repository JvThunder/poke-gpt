import axios from 'axios';

// Use the environment variable with a fallback value
const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:5000/api';

// Create axios instance with default config
const axiosInstance = axios.create({
    baseURL: API_URL,
    headers: {
        'Content-Type': 'application/json',
        'Accept': 'application/json'
    },
    withCredentials: true, // Enable cookies for all requests
    timeout: 30000, // 30 seconds timeout
});

// Add request interceptor for logging
axiosInstance.interceptors.request.use(
    (config) => {
        console.log(`Request: ${config.method.toUpperCase()} ${config.url}`);
        return config;
    },
    (error) => {
        console.error('Request error:', error);
        return Promise.reject(error);
    }
);

// Add response interceptor for error handling
axiosInstance.interceptors.response.use(
    (response) => {
        return response;
    },
    (error) => {
        if (error.response) {
            // The request was made and the server responded with an error status
            console.error(`Error ${error.response.status}: ${error.response.data.error || 'Unknown error'}`);
        } else if (error.request) {
            // The request was made but no response was received
            console.error('No response received from server');
        } else {
            // Something happened in setting up the request
            console.error('Error setting up request:', error.message);
        }
        return Promise.reject(error);
    }
);

// Function to send a message
const sendMessage = (query, chatId) => {
    const payload = { query, chat_id: chatId };
    // The backend endpoint for sending a message is '/query'
    return axiosInstance.post('/query', payload);
};

// Function to get chat history
const getChatHistory = async (chatId) => {
    const response = await axiosInstance.get(`/chat_history/${chatId}`);
    return response;
};

// Function to create a new chat
const createChat = () => {
    return axiosInstance.post('/create_chat', {}, { withCredentials: true });
};

// Function to get user favorites
const getFavorites = async () => {
    const response = await axiosInstance.get('/favorites', { withCredentials: true });
    return response;
};

// Function to remove a pokemon from favorites
const removeFavorite = async (pokemonId) => {
    const response = await axiosInstance.post('/remove_favorite', { pokemon_id: pokemonId }, { withCredentials: true });
    return response;
};

// Function to add a pokemon to favorites
const addToFavorites = async (pokemonName) => {
    const response = await axiosInstance.post('/add_favorite', { pokemon_name: pokemonName }, { withCredentials: true });
    return response;
};

// Function to remove a pokemon from favorites by name
const removeFavoriteByName = async (pokemonName) => {
    const response = await axiosInstance.post('/remove_favorite_by_name', { pokemon_name: pokemonName }, { withCredentials: true });
    return response;
};

// Function to get favorites for a specific user
const getUserFavorites = async (userId) => {
    const response = await axiosInstance.get(`/user_favorites/${userId}`, { withCredentials: true });
    return response;
};

const api = {
    sendMessage,
    getChatHistory,
    createChat,
    getFavorites,
    removeFavorite,
    addToFavorites,
    removeFavoriteByName,
    getUserFavorites,
};

export default api; 