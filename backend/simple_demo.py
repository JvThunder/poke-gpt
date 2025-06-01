import dotenv
dotenv.load_dotenv()

from smolagents import ToolCallingAgent, OpenAIServerModel, tool
import requests

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


model = OpenAIServerModel(model_id='gpt-4o-mini')
agent = ToolCallingAgent(tools=[get_pokemon_list, get_pokemon_details], model=model)

result = agent.run(
    "Can you give me the details of bulbasaur?"
)

print(result)