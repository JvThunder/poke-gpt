from locale import currency
import dotenv
dotenv.load_dotenv()

from smolagents import ToolCallingAgent, OpenAIServerModel, tool
import requests
import uuid
import os
import re
import socket
import favorites_service

# Get Flask API URL from environment or use default
FLASK_API_URL = os.environ.get('FLASK_API_URL', 'http://localhost:5000/api')

SYSTEM_PROMPT = """
You are a helpful Pokémon assistant named PokéGPT. 
Format all your responses using Markdown for better readability.
Use features like:
- **Bold text** for important information
- *Italics* for emphasis
- # Headings for sections
- ## Subheadings for subsections
- Lists (like this one) for multiple items
- `code blocks` for move names or special terms
- Tables for comparing Pokémon stats or abilities

When mentioning a Pokémon name for the first time, use **bold**.
For listing stats or attributes, use tables or bullet points.

## Managing Pokémon Favorites

You can help users manage their favorite Pokémon using these tools:

### Adding Favorites
Use the add_to_favorites tool when a user asks to add a Pokémon to their favorites.

Example requests:
- "Add Pikachu to my favorites"
- "I like Charizard, can you save it for me?"
- "Remember that I like Bulbasaur"

### Removing Favorites
Use the remove_from_favorites tool when a user asks to remove a Pokémon from their favorites.

Example requests:
- "Remove Pikachu from my favorites"
- "I don't like Charizard anymore, can you delete it?"
- "Take Bulbasaur off my list"

### Viewing Favorites
Use the get_user_favorites tool when a user asks to see their favorites list.

Example requests:
- "Show me my favorites"
- "What Pokémon do I have saved?"
- "How many Pokémon are in my favorites?"

You have access to the following tools that you should use to help users:
- get_pokemon_list: Get a list of all Pokémon
- get_pokemon_details: Get detailed information about a specific Pokémon
- get_ability_list: Get a list of all abilities
- get_ability_details: Get detailed information about a specific ability
- add_to_favorites: Add a Pokémon to the user's favorites list
- remove_from_favorites: Remove a Pokémon from the user's favorites list
- get_user_favorites: Get all favorites for a specific user

The currency user's ID is {user_id}.
"""

@tool
def get_pokemon_list() -> list:
    """
    This tool returns the list of all pokemons in this format:
    [
        {
            "name": "bulbasaur",
            "url": "https://pokeapi.co/api/v2/pokemon/1/"
        },
        ...
    ]
    
    You can use this url to get the pokemon details.

    Args:
        query: A search term for finding pokemons.
    Returns:
        A list of pokemons as list of dicts.
    """
    response = requests.get("https://pokeapi.co/api/v2/pokemon?limit=151")
    return response.json()["results"]

@tool 
def get_pokemon_details(id: int) -> dict:
    """
    This tool returns the details of a pokemon in this format:
    {
        "abilities": [...],
        "base_experience": ...,
        "cries": {...},
        "forms": [...],
        "height": ...,
        "held_items": [...],
        "id": ...,
        "is_default": ...,
        "location_area_encounters": ...,
        "moves": [...],
        "types": [...],
        "weight": ...,
    }

    Args:
        id: The id of the pokemon.

    Returns:
        The details of the pokemon in json format.
    """
    response = requests.get(f"https://pokeapi.co/api/v2/pokemon/{id}")
    # remove game indices
    response_json = response.json()
    response_json.pop("game_indices", None)
    # remove version groups from moves
    for move in response_json["moves"]:
        move.pop("version_group_details", None)
    return response_json

@tool
def get_ability_list() -> list:
    """
    This tool returns the list of all abilities in this format:
    [
        {
            "name": "stench",
            "url": "https://pokeapi.co/api/v2/ability/1/"
        },
        ...
    ]

    Args:
        query: A search term for finding abilities.

    Returns:
        A list of abilities as list of dicts.
    """
    response = requests.get("https://pokeapi.co/api/v2/ability?limit=400")
    return response.json()["results"]

@tool
def get_ability_details(id: int) -> dict:
    """
    This tool returns the details of an ability in this format:
    {
        "id": ...,
        "name": "...",
        "effect_entries": [...],
        "flavor_text_entries": [...],
        "generation": {...},
        "names": [...],
        "pokemon": [...]
    }
    
    The response contains detailed information about the ability including:
    - Effect descriptions in multiple languages
    - Flavor text entries from different game versions
    - List of Pokémon that can have this ability
    
    Args:
        id: The id of the ability.

    Returns:
        The details of the ability in json format.
    """
    response = requests.get(f"https://pokeapi.co/api/v2/ability/{id}")
    return response.json()

@tool
def add_to_favorites(pokemon: str, user_id: str) -> str:
    """
    Add a Pokémon to the user's favorites list.
    
    This tool automatically:
    1. Looks up the Pokémon in the PokeAPI database
    2. Retrieves the official Pokémon ID
    3. Adds the Pokémon with correct ID and name to the user's favorites
    4. Persists the favorites data to storage
    
    You should call this tool whenever:
    - A user explicitly asks to add a specific Pokémon to their favorites
    - A user says something like "I like [Pokémon]" and then asks to save it
    - After discussing a Pokémon, the user wants to remember or save it for later
    
    The tool handles normalization of Pokémon names and will inform the user
    if the requested Pokémon cannot be found.
    
    Args:
        pokemon: The name of the Pokémon to add to favorites (e.g., "Pikachu", "Charizard").
                 Case-insensitive and handles basic whitespace issues.
        user_id: The user ID to add the favorite for. IMPORTANT: Always pass the user_id
                 from the context to ensure favorites are saved to the correct account.
        
    Returns:
        A confirmation message with the result of the operation, including the user ID.
    """
    print(f"\n=== TOOL CALLED: add_to_favorites ===")
    print(f"Pokemon: {pokemon}")
    print(f"User ID: {user_id}")
    print(f"======================================\n")
    
    try:
        # Normalize the pokemon name (lowercase and remove spaces)
        normalized_name = pokemon.lower().strip()
        
        # Fetch the pokemon list to get the correct ID
        pokemon_list = get_pokemon_list()
        
        # Find the pokemon in the list
        pokemon_data = None
        pokemon_id = None
        
        for entry in pokemon_list:
            if entry["name"].lower() == normalized_name:
                pokemon_data = entry
                # Extract ID from the URL (format: https://pokeapi.co/api/v2/pokemon/{id}/)
                url_parts = entry["url"].rstrip('/').split('/')
                pokemon_id = int(url_parts[-1])
                break
        
        if not pokemon_id:
            return f"I couldn't find **{pokemon}** in the Pokémon database. Please check the spelling and try again."
        
        # Now add to favorites with the correct ID
        result = favorites_service.add_favorite(pokemon_name=pokemon, pokemon_id=pokemon_id, user_id=user_id)
        
        user_id_str = f"(User ID: {result.get('user_id', 'unknown')})"
        return f"Successfully added **{pokemon}** to your favorites! {user_id_str}"
        
    except Exception as e:
        print(f"Error adding to favorites: {e}")
        return f"I encountered an error while adding **{pokemon}** to your favorites. Please try again. Error: {str(e)}"

@tool
def remove_from_favorites(pokemon: str, user_id: str) -> str:
    """
    Remove a Pokémon from the user's favorites list by name.
    
    This tool automatically:
    1. Normalizes the Pokémon name (case-insensitive search)
    2. Removes the Pokémon from the user's favorites if found
    3. Persists the updated favorites data to storage
    
    You should call this tool whenever:
    - A user explicitly asks to remove a specific Pokémon from their favorites
    - A user says something like "I don't like Charizard anymore, remove it"
    - A user wants to delete or remove a Pokémon from their saved list
    
    Args:
        pokemon: The name of the Pokémon to remove from favorites.
                 Case-insensitive and handles basic whitespace issues.
        user_id: The user ID to remove the favorite from. IMPORTANT: Always pass the user_id
                 from the context to ensure favorites are removed from the correct account.
        
    Returns:
        A confirmation message with the result of the operation.
    """
    print(f"\n=== TOOL CALLED: remove_from_favorites ===")
    print(f"Pokemon: {pokemon}")
    print(f"User ID: {user_id}")
    print(f"======================================\n")
    
    try:
        result = favorites_service.remove_favorite_by_name(pokemon_name=pokemon, user_id=user_id)
        
        if result["success"]:
            return f"Successfully removed **{pokemon}** from your favorites! You now have {result['favorites_count']} Pokémon in your favorites."
        else:
            return f"{result['message']}. Please check the spelling and try again."
            
    except Exception as e:
        print(f"Error removing from favorites: {e}")
        return f"I encountered an error while removing **{pokemon}** from your favorites. Please try again. Error: {str(e)}"

@tool
def get_user_favorites(user_id: str) -> dict:
    """
    Get all favorites for a specific user.
    
    This tool retrieves the complete list of a user's favorite Pokémon.
    
    You should call this tool whenever:
    - A user asks to see their favorites
    - A user asks how many Pokémon they have saved
    - A user wants to check if a specific Pokémon is in their favorites
    
    Args:
        user_id: The user ID to get favorites for. IMPORTANT: Always pass the user_id
                from the context to ensure retrieving the correct user's favorites.
        
    Returns:
        A dictionary containing the user's favorites information.
    """
    print(f"\n=== TOOL CALLED: get_user_favorites ===")
    print(f"User ID: {user_id}")
    print(f"======================================\n")
    
    try:
        result = favorites_service.get_user_favorites(user_id=user_id)
        return result
    except Exception as e:
        print(f"Error getting user favorites: {e}")
        return {
            "error": f"Failed to retrieve favorites: {str(e)}",
            "user_id": user_id,
            "favorites_count": 0,
            "favorites": []
        }

class PokemonAgent:
    def __init__(self):
        # Initialize the model with default settings
        self.model = OpenAIServerModel(model_id='gpt-4o-mini')
        self.tools = [
            get_pokemon_list, 
            get_pokemon_details, 
            get_ability_list, 
            get_ability_details,
            add_to_favorites,
            remove_from_favorites,
            get_user_favorites
        ]
        self.chats = {}  # Dictionary to store chat sessions
        self.tool_calls = []  # Add storage for tool calls

    def create_chat(self, user_id=None):
        """Create a new chat session with a unique ID"""
        print(f"Creating chat session for user {user_id}")
        chat_id = str(uuid.uuid4())
        
        # Create a custom system message that emphasizes using tools
        system_message = SYSTEM_PROMPT.format(user_id=user_id)
        
        self.chats[chat_id] = {
            "agent": ToolCallingAgent(
                tools=self.tools, 
                model=self.model
            ),
            "history": [{
                "role": "system",
                "content": system_message
            }],  # Initialize with enhanced system prompt
            "owner_id": user_id,  # Associate this chat with a specific user
            "tool_calls": [] # Add a list to store tool calls for the session
        }
        
        if user_id:
            print(f"Chat {chat_id} created and associated with user {user_id}")
        
        return chat_id
    
    def run(self, chat_id: str, query: str, user_context: dict = None) -> str:
        """Run a query in a specific chat session and store the interaction"""
        if chat_id not in self.chats:
            raise ValueError(f"Chat session {chat_id} does not exist")
        
        chat = self.chats[chat_id]
            
        # Check if this query is from the chat owner
        current_user_id = user_context.get('current_user_id') if user_context else None
       
        if current_user_id != chat.get('owner_id'):
            raise ValueError(f"User {current_user_id} is not the owner of chat {chat_id}")
        
        print(f"System message: {chat['history'][0]['content']}")

        print(f"\n[QUERY] {query}")
        
        # Call the agent's run method - this handles the entire conversation including tool calls
        print(f"[AGENT] Sending query to model")
        
        response = ""
        tool_calls_this_turn = []


        merged_query = str("Chat Context: " + str(chat["history"]) + "\n" + "User Query: " + query)
        try:
            # Use stream=True to get intermediate steps
            for step in chat["agent"].run(merged_query, stream=True):
                # The 'step' is an ActionStep object. We need to inspect its attributes.
                # Based on smolagents, the tool call info is in the 'action' attribute of the step's model_output_message.
                if hasattr(step, 'model_output_message') and step.model_output_message and hasattr(step.model_output_message, 'tool_calls') and step.model_output_message.tool_calls:
                    for tool_call_data in step.model_output_message.tool_calls:
                        tool_call = {
                            "tool_name": tool_call_data.function.name,
                            "parameters": tool_call_data.function.arguments,
                            "output": step.observations or "No output captured."
                        }
                        tool_calls_this_turn.append(tool_call)
                        chat["tool_calls"].append(tool_call)  # Persist to chat session

                if hasattr(step, 'action_output') and step.action_output:
                    response = str(step.action_output)

            # If the final step didn't have action_output, the result might be the step itself
            if not response and tool_calls_this_turn:
                response = f"I've used the following tools: {', '.join([tc['tool_name'] for tc in tool_calls_this_turn])}."

        except Exception as e:
            print(f"[ERROR] Error during model call: {e}")
            response = f"I apologize, but I encountered an error processing your request. Error details: {str(e)}"
        
        # Store the query and response in history
        chat["history"].append({"role": "user", "content": query})
        chat["history"].append({"role": "assistant", "content": response})
        
        print(f"\n[RESPONSE] {response}")
        
        # Return the response and the tool calls for this turn
        return {
            "response": response,
            "tool_calls": tool_calls_this_turn
        }
    
    def get_chat_history(self, chat_id: str) -> list:
        """Get the chat history for a specific chat session"""
        if chat_id not in self.chats:
            raise ValueError(f"Chat session {chat_id} does not exist")
        
        # Return a simplified version of the history
        simplified_history = []
        for message in self.chats[chat_id]["history"]:
            # Skip temporary system messages about user context
            if message["role"] == "system" and "current user's ID is" in message.get("content", ""):
                continue
            
            # Don't include the initial system prompt in the returned history
            if message["role"] == "system":
                continue
            
            # Create a copy of the message without tool call info
            simplified_message = {
                "role": message["role"],
                "content": message["content"]
            }
            
            simplified_history.append(simplified_message)
        
        return simplified_history
    
    def get_tool_calls(self, chat_id: str) -> list:
        """Get all tool calls for a specific chat session"""
        if chat_id not in self.chats:
            raise ValueError(f"Chat session {chat_id} does not exist")
        
        return self.chats[chat_id].get("tool_calls", [])
        
    def get_chat_owner(self, chat_id: str) -> str:
        """Get the owner ID of a chat session"""
        if chat_id not in self.chats:
            raise ValueError(f"Chat session {chat_id} does not exist")
            
        return self.chats[chat_id].get("owner_id")

if __name__ == "__main__":
    agent = PokemonAgent()
    chat_id = agent.create_chat(user_id="123")
    
    # Example 1: Get Pikachu's abilities
    print("\n===== EXAMPLE 1: GET POKEMON ABILITIES =====")
    print(agent.run(chat_id, "What are the abilities of Pikachu?", user_context={'current_user_id': '123'}))
    
    # Example 2: Add to favorites
    print("\n===== EXAMPLE 2: ADD POKEMON TO FAVORITES =====")
    print(agent.run(chat_id, "Add Pikachu to my favorites", user_context={'current_user_id': '123'}))
    
    # Print all tool calls made during this session
    print("\n===== ALL TOOL CALLS MADE =====")
    for idx, call in enumerate(agent.tool_calls):
        print(f"  {idx+1}. {call['tool']} - Args: {call['args']}")

