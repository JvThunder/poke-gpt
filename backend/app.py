from flask import Flask, request, jsonify
from flask_cors import CORS
import secrets
import os
import sys
import traceback

# Add the parent directory to sys.path to make the import work
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
if parent_dir not in sys.path:
    sys.path.append(parent_dir)

# Try to import with better error handling
try:
    from poke_agent import PokemonAgent
    print("Successfully imported PokemonAgent from poke_agent")
except ImportError as e:
    print(f"ImportError: {e}")
    try:
        from backend.poke_agent import PokemonAgent
        print("Successfully imported PokemonAgent from backend.poke_agent")
    except ImportError as e:
        print(f"ImportError: {e}")
        traceback.print_exc()
        sys.exit(1)

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes
app.secret_key = secrets.token_hex(4)

try:
    pokemon_agent = PokemonAgent()
    print("Successfully created PokemonAgent instance")
except Exception as e:
    print(f"Error creating PokemonAgent: {e}")
    traceback.print_exc()
    sys.exit(1)

@app.route('/')
def index():
    return "Backend is running..."

@app.route('/create_chat', methods=['POST'])
def create_chat():
    """Create a new chat session and return its ID"""
    try:
        chat_id = pokemon_agent.create_chat()
        print(f"Created chat session: {chat_id}")
        return jsonify({'chat_id': chat_id})
    except Exception as e:
        print(f"Error creating chat: {e}")
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500

@app.route('/query', methods=['POST'])
def query():
    """Send a query to a specific chat session"""
    data = request.json
    user_query = data.get('query', '')
    chat_id = data.get('chat_id', '')
    
    if not user_query:
        return jsonify({'error': 'No query provided'}), 400
    
    if not chat_id:
        return jsonify({'error': 'No chat_id provided'}), 400
    
    try:
        response = pokemon_agent.run(chat_id, user_query)
        return jsonify({'response': response})
    except Exception as e:
        print(f"Error processing query: {e}")
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500

@app.route('/chat_history/<chat_id>', methods=['GET'])
def chat_history(chat_id):
    """Get the chat history for a specific chat session"""
    try:
        history = pokemon_agent.get_chat_history(chat_id)
        return jsonify({'history': history})
    except Exception as e:
        print(f"Error getting chat history: {e}")
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    print("Starting Flask server on http://localhost:5000")
    app.run(debug=True, host='0.0.0.0')
