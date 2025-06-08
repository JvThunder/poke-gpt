import './ChatInterface.css';

const ChatInterface = () => {
    const [messages, setMessages] = useState([]);
    const [isLoading, setIsLoading] = useState(false);

    const handleSendMessage = async (userInput) => {
        if (!userInput.trim()) return;

        const newMessages = [...messages, { role: 'user', content: userInput }];
        setMessages(newMessages);
        setIsLoading(true);

        try {
            const response = await api.sendMessage(userInput);
            // The response from the API now includes 'response' and 'tool_calls'
            const assistantMessage = {
                role: 'assistant',
                content: response.response, // The text response
                tool_calls: response.tool_calls || [] // The tool calls
            };
            setMessages([...newMessages, assistantMessage]);
        } catch (error) {
            console.error("Failed to send message:", error);
            const errorMessage = {
                role: 'assistant',
                content: "Sorry, I couldn't get a response. Please try again.",
                isError: true
            };
            setMessages([...newMessages, errorMessage]);
        } finally {
            setIsLoading(false);
        }
    };

    return (
        // ... existing code ...
    );
};

export default ChatInterface; 