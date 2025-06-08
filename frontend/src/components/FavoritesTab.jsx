import React, { useState, useEffect } from 'react';
import api from '../api/axios';
import './FavoritesTab.css';

function FavoritesTab() {
    const [favorites, setFavorites] = useState([]);
    const [favoritesCount, setFavoritesCount] = useState(0);
    const [userId, setUserId] = useState(null);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState(null);

    // Fetch favorites when component mounts
    useEffect(() => {
        fetchFavorites();
    }, []);

    // Fetch favorites from API
    const fetchFavorites = async () => {
        setLoading(true);
        setError(null);

        try {
            console.log('Fetching favorites...');
            const response = await api.getFavorites();
            console.log('Favorites fetched:', response.data);

            // Ensure the response contains the expected data
            if (response.data && Array.isArray(response.data.favorites)) {
                setFavorites(response.data.favorites);
                setFavoritesCount(response.data.favorites.length);
                setUserId(response.data.user_id);
            } else {
                throw new Error('Invalid response format');
            }
        } catch (err) {
            console.error('Error fetching favorites:', err);
            setError('Failed to load favorites. Please try again later.');
        } finally {
            setLoading(false);
        }
    };

    // Remove a favorite
    const removeFavorite = async (pokemonId) => {
        try {
            const response = await api.removeFavorite(pokemonId);
            console.log('Remove favorite response:', response.data);

            // Update local state
            setFavorites(favorites.filter(p => p.id !== pokemonId));
            setFavoritesCount(response.data.favorites_count || favorites.length - 1);
        } catch (err) {
            console.error('Error removing favorite:', err);
            setError('Failed to remove from favorites. Please try again.');
        }
    };

    if (loading) {
        return <div className="favorites-loading">Loading favorites...</div>;
    }

    if (error) {
        return (
            <div className="favorites-error">
                {error}
                <button
                    className="reload-button"
                    onClick={fetchFavorites}
                >
                    Try Again
                </button>
            </div>
        );
    }

    return (
        <div className="favorites-container">
            <h2>Your Favorite Pokémon</h2>

            {favorites.length === 0 ? (
                <div className="no-favorites">
                    <p>You haven't added any Pokémon to your favorites yet.</p>
                    <p>To add a Pokémon to your favorites, ask about a Pokémon and then ask to add it to your favorites.</p>
                    {userId && <p className="user-id-info">Your user ID: {userId.substring(0, 8)}...</p>}
                </div>
            ) : (
                <>
                    <div className="favorites-header">
                        <span>{favoritesCount} Pokémon in favorites</span>
                        <div className="favorites-actions">
                            {userId && <span className="user-id">User: {userId.substring(0, 8)}...</span>}
                            <button
                                className="refresh-button"
                                onClick={fetchFavorites}
                            >
                                Refresh
                            </button>
                        </div>
                    </div>
                    <div className="favorites-grid">
                        {favorites.map(pokemon => (
                            <div key={pokemon.id} className="favorite-card">
                                <img
                                    src={`https://raw.githubusercontent.com/PokeAPI/sprites/master/sprites/pokemon/${pokemon.id}.png`}
                                    alt={pokemon.name}
                                />
                                <h3>{pokemon.name}</h3>
                                <button
                                    className="remove-button"
                                    onClick={() => removeFavorite(pokemon.id)}
                                >
                                    Remove
                                </button>
                            </div>
                        ))}
                    </div>
                </>
            )}
        </div>
    );
}

export default FavoritesTab; 