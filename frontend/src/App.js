import React, { useState } from 'react';
import WebSocketLogger from './WebSocketLogger';
import './App.css';

function App() {
  const [prompt, setPrompt] = useState("");
  const [chatLog, setChatLog] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const sendPrompt = async () => {
    if (!prompt.trim()) return;
    
    setLoading(true);
    setError(null);
    
    // Add user message to chat log immediately
    const userMessage = { type: 'user', content: prompt };
    setChatLog(prev => [...prev, userMessage]);
    
    try {
      const response = await fetch("http://localhost:8000/chat", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          "X-API-Key": "mysecretapikey" // Must match backend API key
        },
        body: JSON.stringify({ user: "testUser", prompt })
      });
      
      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.detail || "Error communicating with the server");
      }
      
      const data = await response.json();
      
      // Add AI response to chat log
      const aiMessage = { 
        type: 'ai', 
        content: data.response, 
        model: data.model_used,
        tokens: data.tokens_used,
        cost: data.cost
      };
      
      setChatLog(prev => [...prev, aiMessage]);
      setPrompt("");
    } catch (error) {
      console.error("Error sending prompt:", error);
      setError(error.message);
    } finally {
      setLoading(false);
    }
  };

  const handleKeyPress = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      sendPrompt();
    }
  };

  return (
    <div className="App">
      <header>
        <h1>Multi‑Model AI Router</h1>
        <p>Intelligent routing to the best AI model for your query</p>
      </header>
      
      <main>
        <div className="chat-container">
          <div className="messages">
            {chatLog.length === 0 ? (
              <div className="empty-state">
                <p>Send a message to start chatting with AI models</p>
                <p className="hint">Try asking about code, creative writing, or research questions!</p>
              </div>
            ) : (
              chatLog.map((message, index) => (
                <div key={index} className={`message ${message.type}-message`}>
                  {message.type === 'user' ? (
                    <>
                      <div className="message-header">
                        <strong>You</strong>
                      </div>
                      <div className="message-content">{message.content}</div>
                    </>
                  ) : (
                    <>
                      <div className="message-header">
                        <strong>AI ({message.model})</strong>
                        <span className="message-meta">
                          {message.tokens} tokens (${message.cost.toFixed(6)})
                        </span>
                      </div>
                      <div className="message-content">{message.content}</div>
                    </>
                  )}
                </div>
              ))
            )}
            
            {error && (
              <div className="error-message">
                <strong>Error:</strong> {error}
              </div>
            )}
            
            {loading && (
              <div className="loading-indicator">
                <div className="loading-spinner"></div>
                <span>AI is thinking...</span>
              </div>
            )}
          </div>
          
          <div className="input-area">
            <textarea 
              value={prompt}
              onChange={(e) => setPrompt(e.target.value)}
              placeholder="Enter your prompt..."
              onKeyPress={handleKeyPress}
              disabled={loading}
              rows={1}
            />
            <button 
              onClick={sendPrompt} 
              disabled={loading || !prompt.trim()}
              className={loading ? "loading" : ""}
            >
              {loading ? "Sending..." : "Send"}
            </button>
          </div>
        </div>
        
        <WebSocketLogger />
      </main>
      
      <footer>
        <p>Model Router Demo - Connects to real AI models</p>
      </footer>
    </div>
  );
}

export default App;
