import sys
from pathlib import Path
sys.path.append(str(Path(__file__).resolve().parent.parent))

import os
import traceback
import json
from poke_agent import PokemonAgent
import favorites_service
from flask import Flask, request, jsonify, make_response, render_template, session
from flask_cors import CORS
import secrets

app = Flask(__name__, static_folder='../frontend/build', static_url_path='/')
CORS(app, supports_credentials=True)  # Enable CORS for all routes with credentials
app.secret_key = secrets.token_hex(4)

try:
    pokemon_agent = PokemonAgent()
    print("Successfully created PokemonAgent instance")
except Exception as e:
    print(f"Error creating PokemonAgent: {e}")
    traceback.print_exc()
    sys.exit(1)

@app.route('/api/')
def index():
    return "Backend is running..."

def get_or_create_user_id():
    """Get user ID from cookie or create a new one"""
    user_id = request.cookies.get('user_id')
    if not user_id:
        user_id = str(secrets.token_hex(16))
        print(f"Generated new user ID: {user_id}")
        # Initialize empty favorites for new user
        favorites_service.favorites_db[user_id] = []
    elif user_id not in favorites_service.favorites_db:
        # Initialize favorites for existing user with no favorites
        print(f"Initializing favorites for existing user: {user_id}")
        favorites_service.favorites_db[user_id] = []
    else:
        print(f"Using existing user: {user_id} with {len(favorites_service.favorites_db[user_id])} favorites")
    return user_id

@app.route('/api/create_chat', methods=['POST'])
def create_chat():
    """Create a new chat session and return its ID"""
    try:
        # Get or create user ID
        user_id = get_or_create_user_id()
        
        # Create chat session with associated user_id
        chat_id = pokemon_agent.create_chat(user_id=user_id)
        print(f"Created chat session: {chat_id} for user: {user_id}")
        
        # Create response with chat ID
        response = jsonify({'chat_id': chat_id, 'user_id': user_id})
        
        # Set user ID cookie if it doesn't exist
        if not request.cookies.get('user_id'):
            response.set_cookie('user_id', user_id, max_age=31536000, httponly=True, samesite='Lax')
        
        return response
    except Exception as e:
        print(f"Error creating chat: {e}")
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500

@app.route('/api/query', methods=['POST'])
def query():
    """Send a query to a specific chat session"""
    data = request.json
    user_query = data.get('query', '')
    chat_id = data.get('chat_id', '')
    user_id = data.get('user_id') or request.cookies.get('user_id')
    
    if not user_query:
        return jsonify({'error': 'No query provided'}), 400
    
    if not chat_id:
        chat_id = pokemon_agent.create_chat(user_id=user_id)
        session['chat_id'] = chat_id

    # Provide the user_id in the user_context
    user_context = {'current_user_id': user_id}
    
    # The run method now returns a dictionary
    result = pokemon_agent.run(chat_id, user_query, user_context)
    
    # The response now includes the text and tool calls
    return jsonify({
        "response": result.get("response"),
        "tool_calls": result.get("tool_calls", [])
    })

@app.route('/api/chat_history/<chat_id>', methods=['GET'])
def chat_history(chat_id):
    """Get the chat history for a specific chat session"""
    try:
        history = pokemon_agent.get_chat_history(chat_id)
        # remove system prompt from history
        history = history[1:] if history and history[0]["role"] == "system" else history
        
        # Get the owner ID of this chat
        owner_id = pokemon_agent.get_chat_owner(chat_id)
        
        # Get current user ID from cookie
        current_user_id = request.cookies.get('user_id')
        
        # Check if current user is the owner
        is_owner = owner_id == current_user_id if owner_id and current_user_id else False
        
        return jsonify({
            'history': history,
            'owner_id': owner_id,
            'is_owner': is_owner
        })
    except Exception as e:
        print(f"Error getting chat history: {e}")
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500

@app.route('/api/add_favorite', methods=['POST'])
def add_favorite():
    """API endpoint to add a Pokémon to the user's favorites."""
    data = request.json
    pokemon_name = data.get('pokemon_name')
    user_id = data.get('user_id') or get_or_create_user_id()

    if not pokemon_name:
        return jsonify({"error": "Pokemon name is required"}), 400

    try:
        result = favorites_service.add_favorite(pokemon_name=pokemon_name, user_id=user_id)
        # Save to file
        save_favorites()
        return jsonify(result), 200
    except Exception as e:
        return jsonify({"error": f"An unexpected error occurred: {str(e)}"}), 500

@app.route('/api/favorites', methods=['GET'])
def get_favorites():
    """API endpoint to get the favorites for the current user."""
    user_id = request.cookies.get('user_id') 
    print(f"Getting favorites for user {user_id}")
    if not user_id:
        return jsonify({"user_id": None, "favorites": []})  # Return empty list if no user session
        
    favorites_data = favorites_service.get_favorites(user_id)
    return jsonify(favorites_data)

@app.route('/api/remove_favorite', methods=['POST'])
def remove_favorite():
    """Remove a Pokémon from user favorites"""
    data = request.json
    pokemon_id = data.get('pokemon_id')
    
    if not pokemon_id:
        return jsonify({'error': 'Pokemon ID is required'}), 400
    
    # Get user ID from cookie
    user_id = get_or_create_user_id()
    
    # Remove from favorites if exists
    if user_id in favorites_service.favorites_db:
        before_count = len(favorites_service.favorites_db[user_id])
        favorites_service.favorites_db[user_id] = [p for p in favorites_service.favorites_db[user_id] if p.get('id') != pokemon_id]
        after_count = len(favorites_service.favorites_db[user_id])
        
        if before_count > after_count:
            print(f"Removed pokemon ID {pokemon_id} from user {user_id}'s favorites")
        else:
            print(f"Pokemon ID {pokemon_id} not found in user {user_id}'s favorites")
        
    # Save to file
    favorites_service.save_favorites()
    
    return jsonify({
        'success': True, 
        'message': 'Removed from favorites',
        'user_id': user_id,
        'favorites_count': len(favorites_service.favorites_db.get(user_id, []))
    })

@app.route('/api/chats/<chat_id>/tool_calls', methods=['GET'])
def get_chat_tool_calls(chat_id):
    """API endpoint to get all tool calls for a specific chat session."""
    user_id = get_or_create_user_id()
    chat_owner = pokemon_agent.get_chat_owner(chat_id)

    if user_id != chat_owner:
        return jsonify({"error": "Unauthorized"}), 403

    tool_calls = pokemon_agent.get_tool_calls(chat_id)
    return jsonify(tool_calls)

@app.route('/api/remove_favorite_by_name', methods=['POST'])
def remove_favorite_by_name():
    """Remove a Pokémon from user favorites by name"""
    data = request.json
    pokemon_name = data.get('pokemon_name')
    
    if not pokemon_name:
        return jsonify({'error': 'Pokemon name is required'}), 400
    
    # Get user ID from cookie
    user_id = get_or_create_user_id()
    
    # Remove from favorites by name
    result = favorites_service.remove_favorite_by_name(pokemon_name=pokemon_name, user_id=user_id)
    
    return jsonify(result)

@app.route('/api/user_favorites/<user_id>', methods=['GET'])
def get_user_favorites(user_id):
    """Get all favorites for a specific user"""
    # Check if the requester is the same as the target user
    current_user_id = request.cookies.get('user_id')
    
    # Only allow if the user is requesting their own favorites or no user ID provided
    if current_user_id != user_id and current_user_id:
        return jsonify({"error": "Unauthorized to view another user's favorites"}), 403
    
    # Get favorites for the user
    result = favorites_service.get_user_favorites(user_id=user_id)
    
    return jsonify(result)

if __name__ == '__main__':
    print("Starting Flask server")
    app.run(debug=True, host='0.0.0.0')
