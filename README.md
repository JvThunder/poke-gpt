# PokéGPT

A chat application that allows you to interact with a Pokémon-focused AI assistant. Ask questions about Pokémon, their abilities, and more!

## Features

- Chat interface with persistent sessions
- Memory of conversation context
- Information about Pokémon and abilities
- Modern and responsive UI

## Project Structure

```
poke-gpt/
├── backend/
│   ├── app.py           # Flask API endpoints
│   └── poke_agent.py    # PokemonAgent class with tools
├── frontend/
│   ├── public/          # Static files
│   └── src/             # React components
│       ├── components/  # UI components
│       ├── App.jsx      # Main application component
│       └── main.jsx     # Entry point
└── requirements.txt     # Python dependencies
```

## Docker Setup

The application can be run using Docker and Docker Compose for easy deployment.

### Production Setup

Build and run the application in production mode:

```bash
docker-compose up --build
```

The frontend will be available at http://localhost:3000 and the backend at http://localhost:5000.

### Development Setup

Build and run the application in development mode:

```bash
docker-compose -f docker-compose.dev.yml up --build
```

The frontend will be available at http://localhost:5173 with hot-reload enabled, and the backend at http://localhost:5000.

## Manual Setup

### Backend

1. Navigate to the backend directory:
   ```bash
   cd backend
   ```

2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Run the backend:
   ```bash
   python app.py
   ```

### Frontend

1. Navigate to the frontend directory:
   ```bash
   cd frontend
   ```

2. Install dependencies:
   ```bash
   npm install
   ```

3. Run the development server:
   ```bash
   npm run dev
   ```

4. For production build:
   ```bash
   npm run build
   ```

## Usage

1. Open your browser and go to http://localhost:5173
2. A new chat session will be created automatically
3. Type your Pokémon-related questions in the input box
4. Press Enter or click the send button to submit
5. Use the "New Chat" button to start a fresh conversation

## API Endpoints

- `POST /create_chat`: Create a new chat session
- `POST /query`: Send a message to a specific chat session
- `GET /chat_history/<chat_id>`: Get chat history for a specific session

## Technologies Used

- **Backend**: Flask, smolagents, OpenAI
- **Frontend**: React, Vite, Axios
- **API**: PokeAPI
