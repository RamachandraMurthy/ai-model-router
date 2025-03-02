import React, { useState, useEffect } from 'react';

const WebSocketLogger = () => {
  const [logs, setLogs] = useState([]);
  const [connected, setConnected] = useState(false);
  
  useEffect(() => {
    // Connect to the backend WebSocket endpoint
    const ws = new WebSocket("ws://localhost:8000/ws/logs");
    
    ws.onopen = () => {
      console.log("WebSocket connected");
      // Send API key for authentication
      ws.send(JSON.stringify({ 
        type: "authentication", 
        api_key: "mysecretapikey" 
      }));
    };
    
    ws.onmessage = (event) => {
      const message = event.data;
      
      // Check for authentication success
      if (message === "Authentication successful") {
        setConnected(true);
        setLogs(prev => [...prev, "Connected to log stream"]);
      } 
      // Check for authentication failure
      else if (message.includes("Authentication failed")) {
        setLogs(prev => [...prev, "Failed to connect: " + message]);
      }
      // Regular log message
      else {
        setLogs(prev => [...prev, message]);
      }
    };
    
    ws.onerror = (error) => {
      console.error("WebSocket error", error);
      setLogs(prev => [...prev, "Error: Connection failed"]);
    };
    
    ws.onclose = () => {
      console.log("WebSocket disconnected");
      setConnected(false);
      setLogs(prev => [...prev, "Disconnected from log stream"]);
    };
    
    return () => {
      ws.close();
    };
  }, []);
  
  return (
    <div className="logs">
      <h2>Real-Time Logs {connected ? "(Connected)" : "(Disconnected)"}</h2>
      <div style={{ maxHeight: "150px", overflowY: "scroll", border: "1px solid #ccc", padding: "8px", backgroundColor: "#f5f5f5" }}>
        {logs.length === 0 ? (
          <div>Waiting for logs...</div>
        ) : (
          logs.map((log, idx) => (
            <div key={idx} style={{ fontFamily: "monospace", fontSize: "0.9em" }}>{log}</div>
          ))
        )}
      </div>
    </div>
  );
};

export default WebSocketLogger;
