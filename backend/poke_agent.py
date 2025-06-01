import dotenv
dotenv.load_dotenv()

from smolagents import ToolCallingAgent, OpenAIServerModel, tool
import requests
import uuid

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
        "game_indices": [...],
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
    return response.json()

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

class PokemonAgent:
    def __init__(self):
        self.model = OpenAIServerModel(model_id='gpt-4o-mini')
        self.tools = [
            get_pokemon_list, 
            get_pokemon_details, 
            get_ability_list, 
            get_ability_details
        ]
        self.chats = {}  # Dictionary to store chat sessions

    def create_chat(self):
        """Create a new chat session with a unique ID"""
        chat_id = str(uuid.uuid4())
        self.chats[chat_id] = {
            "agent": ToolCallingAgent(tools=self.tools, model=self.model),
            "history": []  # Store messages directly in the format needed by the model
        }
        return chat_id

    def run(self, chat_id: str, query: str) -> str:
        """Run a query in a specific chat session and store the interaction"""
        if chat_id not in self.chats:
            raise ValueError(f"Chat session {chat_id} does not exist")
        
        # Add user query to history in the correct format
        self.chats[chat_id]["history"].append({
            "role": "user",
            "content": [{"type": "text", "text": query}]
        })
        
        # Use the history directly without reformatting
        response = self.chats[chat_id]["agent"].model(self.chats[chat_id]["history"]).content
        
        # Add agent response to history in the correct format
        self.chats[chat_id]["history"].append({
            "role": "assistant",
            "content": [{"type": "text", "text": response}]
        })
        
        return response
    
    def get_chat_history(self, chat_id: str) -> list:
        """Get the chat history for a specific chat session"""
        if chat_id not in self.chats:
            raise ValueError(f"Chat session {chat_id} does not exist")
        
        # Convert the formatted history back to the simple format for the API
        simplified_history = []
        for message in self.chats[chat_id]["history"]:
            # Extract the text content from the formatted message
            content = message["content"][0]["text"] if isinstance(message["content"], list) else message["content"]
            simplified_history.append({
                "role": message["role"],
                "content": content
            })
        
        return simplified_history

if __name__ == "__main__":
    agent = PokemonAgent()
    chat_id = agent.create_chat()
    print(agent.run(chat_id, "Can you give me the details of bulbasaur?"))

