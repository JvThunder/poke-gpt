import axios from 'axios';

// Use the environment variable with a fallback value
const API_URL = process.env.VITE_API_URL || 'https://poke-gpt.jvthunder.org/api';

// Create axios instance with default config
const api = axios.create({
    baseURL: API_URL,
    headers: {
        'Content-Type': 'application/json',
    },
    timeout: 10000, // 10 seconds timeout
});

export default api; 