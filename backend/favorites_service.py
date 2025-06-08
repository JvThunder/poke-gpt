import uuid
import re
import os
import json

# In-memory storage for favorites (replace with a real database in production)
favorites_db = {}

# File to store user favorites
FAVORITES_FILE = os.path.join(os.path.dirname(__file__), 'user_favorites.json')

# Load favorites from file if it exists
def load_favorites():
    try:
        if os.path.exists(FAVORITES_FILE):
            with open(FAVORITES_FILE, 'r') as f:
                loaded_favorites = json.load(f)
                # Update favorites_service's database with loaded data
                favorites_db.update(loaded_favorites)
            print(f"Loaded {len(favorites_db)} user favorites from file")
        else:
            print("No favorites file found, starting with empty favorites")
    except Exception as e:
        print(f"Error loading favorites: {e}")

# Save favorites to file
def save_favorites():
    try:
        with open(FAVORITES_FILE, 'w') as f:
            json.dump(favorites_db, f)
        print(f"Saved {len(favorites_db)} user favorites to file")
    except Exception as e:
        print(f"Error saving favorites: {e}")

# Load favorites on startup
load_favorites()

def add_favorite(pokemon_name: str, pokemon_id: int = None, user_id: str = None) -> dict:
    """
    Adds a pokemon to the favorites list for a given user.
    If user_id is not provided, a new one is generated.
    If pokemon_id is not provided, attempts to extract it from the name or generates one.
    """
    if not user_id:
        user_id = str(uuid.uuid4())
        
    if user_id not in favorites_db:
        favorites_db[user_id] = []
    
    # Clean the pokemon name (capitalize first letter)
    clean_name = pokemon_name.strip().capitalize()
    
    # If pokemon_id is not provided, try to extract from name or generate one
    if pokemon_id is None:
        # Extract pokemon ID from name if it has a format like "bulbasaur-1"
        if "-" in pokemon_name:
            match = re.search(r'-(\d+)$', pokemon_name)
            if match:
                pokemon_id = int(match.group(1))
                # Clean the name by removing the ID part
                clean_name = pokemon_name.split('-')[0].capitalize()
        
        # If still no ID found, use a simple hash of the name as the ID
        if pokemon_id is None:
            # Using a simple hash to generate a stable ID from the name
            # This is a simplified approach - in a real app, you'd query the PokeAPI
            pokemon_id = abs(hash(clean_name.lower())) % 1000
    
    # Create pokemon object with id and name
    pokemon_obj = {
        "id": pokemon_id,
        "name": clean_name
    }
    
    # Check if this pokemon is already in favorites
    already_exists = any(p.get('id') == pokemon_id for p in favorites_db[user_id])
    
    if not already_exists:
        favorites_db[user_id].append(pokemon_obj)
        
    print(f"\n[SERVICE] Favorites for user {user_id}: {favorites_db[user_id]}")
    save_favorites()

    return {
        "user_id": user_id,
        "favorites": favorites_db[user_id],
        "message": f"Added {clean_name} to favorites."
    }

def remove_favorite_by_name(pokemon_name: str, user_id: str) -> dict:
    """
    Removes a pokemon from the favorites list by name for a given user.
    
    Args:
        pokemon_name: The name of the Pokemon to remove
        user_id: The user ID to remove the favorite from
        
    Returns:
        A dictionary with the result of the operation
    """
    if not user_id or user_id not in favorites_db:
        return {
            "success": False,
            "message": "User not found or has no favorites",
            "user_id": user_id,
            "favorites_count": 0,
            "favorites": []
        }
    
    # Normalize the pokemon name for comparison
    normalized_name = pokemon_name.strip().lower()
    
    before_count = len(favorites_db[user_id])
    favorites_db[user_id] = [p for p in favorites_db[user_id] if p.get('name', '').lower() != normalized_name]
    after_count = len(favorites_db[user_id])
    
    if before_count > after_count:
        print(f"Removed pokemon '{pokemon_name}' from user {user_id}'s favorites")
        save_favorites()
        return {
            "success": True,
            "message": f"Removed {pokemon_name} from favorites",
            "user_id": user_id,
            "favorites_count": after_count,
            "favorites": favorites_db[user_id]
        }
    else:
        print(f"Pokemon '{pokemon_name}' not found in user {user_id}'s favorites")
        return {
            "success": False,
            "message": f"Could not find {pokemon_name} in your favorites",
            "user_id": user_id,
            "favorites_count": after_count,
            "favorites": favorites_db[user_id]
        }

def get_user_favorites(user_id: str) -> dict:
    """
    Retrieves the favorites list for a specific user.
    
    Args:
        user_id: The user ID to get favorites for
        
    Returns:
        A dictionary with the user's favorites information
    """
    if not user_id or user_id not in favorites_db:
        return {
            "user_id": user_id,
            "favorites_count": 0,
            "favorites": []
        }
    
    favorites = favorites_db.get(user_id, [])
    return {
        "user_id": user_id,
        "favorites_count": len(favorites),
        "favorites": favorites
    }

def get_favorites(user_id: str) -> dict:
    """
    Retrieves the favorites list for a given user.
    """
    favorites = favorites_db.get(user_id, [])
    return {
        "user_id": user_id,
        "favorites": favorites
    }