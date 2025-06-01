import { useState, useEffect } from 'react'
import api from './api/axios'
import './App.css'
import ChatInterface from './components/ChatInterface.jsx'
import Header from './components/Header.jsx'

function App() {
  const [chatId, setChatId] = useState(null)
  const [isLoading, setIsLoading] = useState(false)
  const [error, setError] = useState(null)
  const [retryCount, setRetryCount] = useState(0)

  // Create a new chat session when the app loads
  useEffect(() => {
    createNewChat()
  }, [])

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
      const response = await api.post('/create_chat', {})

      console.log('Chat session created:', response.data)
      setChatId(response.data.chat_id)
      setRetryCount(0) // Reset retry count on success
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

  return (
    <div className="app">
      <Header onNewChat={createNewChat} />
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
        {isLoading && !chatId ? (
          <div className="loading">Creating chat session...</div>
        ) : (
          chatId && <ChatInterface chatId={chatId} />
        )}
      </main>
    </div>
  )
}

export default App
