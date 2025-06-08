import { useState, useEffect, useCallback } from 'react'
import api from './api/axios'
import './App.css'
import ChatInterface from './components/ChatInterface.jsx'
import FavoritesTab from './components/FavoritesTab.jsx'
import Header from './components/Header.jsx'

function App() {
  const [chatId, setChatId] = useState(null)
  const [isLoading, setIsLoading] = useState(false)
  const [error, setError] = useState(null)
  const [retryCount, setRetryCount] = useState(0)
  const [activeTab, setActiveTab] = useState('chat') // 'chat' or 'favorites'
  const [favoritesKey, setFavoritesKey] = useState(0) // Used to force refresh FavoritesTab
  const [favoritesCount, setFavoritesCount] = useState(0) // Store favorites count
  const [userId, setUserId] = useState(null) // Store user ID

  // Function to fetch favorites count
  const fetchFavoritesCount = useCallback(async () => {
    try {
      const response = await api.getFavorites();
      if (response.data && Array.isArray(response.data.favorites)) {
        setFavoritesCount(response.data.favorites.length);
        if (response.data.user_id) {
          setUserId(response.data.user_id);
        }
      }
    } catch (err) {
      console.error('Error fetching favorites count:', err);
    }
  }, []);

  // Function to refresh the favorites tab and count
  const refreshFavorites = useCallback(() => {
    setFavoritesKey(prevKey => prevKey + 1);
    fetchFavoritesCount();
  }, [fetchFavoritesCount]);

  // Fetch favorites count on initial load
  useEffect(() => {
    fetchFavoritesCount();

    // Set up interval to refresh count every 30 seconds
    const intervalId = setInterval(fetchFavoritesCount, 30000);

    return () => clearInterval(intervalId);
  }, [fetchFavoritesCount]);

  // Check for chat ID in URL or create a new chat session when the app loads
  useEffect(() => {
    const params = new URLSearchParams(window.location.search)
    const chatIdFromUrl = params.get('chatId')

    if (chatIdFromUrl) {
      console.log('Using chat ID from URL:', chatIdFromUrl)
      setChatId(chatIdFromUrl)
    } else {
      console.log('No chat ID in URL, creating new chat')
      createNewChat()
    }
  }, [])

  // Update URL when chat ID changes
  useEffect(() => {
    if (chatId) {
      // Update URL without reloading page
      const url = new URL(window.location)
      url.searchParams.set('chatId', chatId)
      window.history.pushState({}, '', url)
    }
  }, [chatId])

  // Retry creating a chat session if it fails
  useEffect(() => {
    if (error && retryCount < 3) {
      const timer = setTimeout(() => {
        console.log(`Retrying chat creation (attempt ${retryCount + 1})`)
        createNewChat()
        setRetryCount(prevCount => prevCount + 1)
      }, 2000) // Retry after 2 seconds

      return () => clearTimeout(timer)
    }
  }, [error, retryCount])

  // Function to create a new chat session
  const createNewChat = async () => {
    setIsLoading(true)
    setError(null)

    try {
      console.log('Creating new chat session...')
      const response = await api.createChat()

      console.log('Chat session created:', response.data)
      setChatId(response.data.chat_id)
      setRetryCount(0) // Reset retry count on success
      setActiveTab('chat') // Switch to chat tab when creating a new chat
    } catch (err) {
      console.error('Error creating chat:', err)
      setError('Failed to create chat session. Please try again.')
    } finally {
      setIsLoading(false)
    }
  }

  const handleRetry = () => {
    setRetryCount(0)
    createNewChat()
  }

  const handleTabChange = (tab) => {
    setActiveTab(tab)
    // Refresh favorites when switching to the favorites tab
    if (tab === 'favorites') {
      refreshFavorites()
    }
  }

  return (
    <div className="app">
      <Header
        onNewChat={createNewChat}
        activeTab={activeTab}
        onTabChange={handleTabChange}
        favoritesCount={favoritesCount}
      />
      <main className="container">
        {error && (
          <div className="error-message">
            {error}
            <button
              className="retry-button"
              onClick={handleRetry}
              disabled={isLoading}
            >
              Retry
            </button>
          </div>
        )}
        {activeTab === 'chat' ? (
          isLoading && !chatId ? (
            <div className="loading">Creating chat session...</div>
          ) : (
            chatId && <ChatInterface chatId={chatId} refreshFavorites={refreshFavorites} userId={userId} />
          )
        ) : (
          <FavoritesTab key={favoritesKey} />
        )}
      </main>
    </div>
  )
}

export default App
