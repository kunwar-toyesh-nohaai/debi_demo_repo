import { useState, useEffect, useRef } from 'react';
import './App.css';

interface Message {
  role: 'user' | 'assistant' | 'status';
  content: string;
  timestamp: string;
}

const WEBSOCKET_URL = 'ws://localhost:8000/ws/chat';

function App() {
  const [messages, setMessages] = useState<Message[]>([]);
  const [input, setInput] = useState('');
  const [isConnected, setIsConnected] = useState(false);
  const [isSending, setIsSending] = useState(false);
  const wsRef = useRef<WebSocket | null>(null);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  useEffect(() => {
    connectWebSocket();
    
    return () => {
      if (wsRef.current) {
        wsRef.current.close();
      }
    };
  }, []);

  const connectWebSocket = () => {
    try {
      const ws = new WebSocket(WEBSOCKET_URL);
      
      ws.onopen = () => {
        console.log('WebSocket connected');
        setIsConnected(true);
      };
      
      ws.onmessage = (event) => {
        const data = JSON.parse(event.data);
        
        if (data.type === 'message' || data.type === 'request_directory') {
          setMessages((prev) => [
            ...prev,
            {
              role: data.role,
              content: data.content,
              timestamp: data.timestamp,
            },
          ]);
          setIsSending(false);
        } else if (data.type === 'status') {
          setMessages((prev) => [
            ...prev,
            {
              role: 'status',
              content: data.content,
              timestamp: data.timestamp,
            },
          ]);
        } else if (data.type === 'error') {
          setMessages((prev) => [
            ...prev,
            {
              role: 'assistant',
              content: `⚠️ ${data.content}`,
              timestamp: data.timestamp,
            },
          ]);
          setIsSending(false);
        }
      };
      
      ws.onerror = (error) => {
        console.error('WebSocket error:', error);
        setIsConnected(false);
      };
      
      ws.onclose = () => {
        console.log('WebSocket disconnected');
        setIsConnected(false);
        
        // Attempt to reconnect after 3 seconds
        setTimeout(() => {
          console.log('Attempting to reconnect...');
          connectWebSocket();
        }, 3000);
      };
      
      wsRef.current = ws;
    } catch (error) {
      console.error('Failed to connect WebSocket:', error);
      setIsConnected(false);
    }
  };

  const sendMessage = () => {
    if (!input.trim() || !isConnected || isSending) return;
    
    const userMessage: Message = {
      role: 'user',
      content: input.trim(),
      timestamp: new Date().toISOString(),
    };
    
    setMessages((prev) => [...prev, userMessage]);
    setIsSending(true);
    
    if (wsRef.current && wsRef.current.readyState === WebSocket.OPEN) {
      wsRef.current.send(
        JSON.stringify({
          type: 'message',
          content: input.trim(),
        })
      );
    }
    
    setInput('');
  };

  const handleKeyPress = (e: React.KeyboardEvent<HTMLTextAreaElement>) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      sendMessage();
    }
  };

  const useExamplePrompt = (prompt: string) => {
    setInput(prompt);
  };

  const examplePrompts = [
    {
      title: '🐛 Fix a Bug',
      description: 'Help me debug an issue in my code',
      prompt: 'I have a bug where my login function throws a KeyError when the user doesn\'t provide an email field',
    },
    {
      title: '✨ Add a Feature',
      description: 'Implement a new functionality',
      prompt: 'Add user authentication to my Flask application',
    },
    {
      title: '🔍 Code Review',
      description: 'Review and improve code quality',
      prompt: 'Review my API endpoint code and suggest improvements for security and performance',
    },
  ];

  return (
    <div className="app">
      <header className="app-header">
        <h1>
          <span className="logo-icon">🤖</span>
          <span className="gradient-text">Debi AI Agent</span>
        </h1>
        <div className="connection-status">
          <span className={`status-indicator ${isConnected ? 'connected' : 'disconnected'}`}></span>
          <span>{isConnected ? 'Connected' : 'Disconnected'}</span>
        </div>
      </header>

      <div className="chat-container">
        {messages.length === 0 ? (
          <div className="empty-state">
            <div className="empty-state-icon">💬</div>
            <h2 className="gradient-text">Welcome to Debi AI</h2>
            <p>
              I'm your AI coding assistant. I can help you debug code, add features, review your work, 
              and much more. Just describe what you need!
            </p>
            <div className="example-prompts">
              {examplePrompts.map((example, index) => (
                <div
                  key={index}
                  className="example-prompt glassmorphism hover-lift"
                  onClick={() => useExamplePrompt(example.prompt)}
                >
                  <div className="example-prompt-title">{example.title}</div>
                  <div className="example-prompt-description">{example.description}</div>
                </div>
              ))}
            </div>
          </div>
        ) : (
          <div className="messages-container">
            {messages.map((message, index) => (
              <div key={index}>
                {message.role === 'status' ? (
                  <div className="message-status">
                    <div className="spinner"></div>
                    {message.content}
                  </div>
                ) : (
                  <div className={`message ${message.role}`}>
                    <div className="message-avatar">
                      {message.role === 'user' ? '👤' : '🤖'}
                    </div>
                    <div className="message-content">
                      {message.content}
                    </div>
                  </div>
                )}
              </div>
            ))}
            <div ref={messagesEndRef} />
          </div>
        )}
      </div>

      <div className="input-container">
        <div className="input-wrapper">
          <div className="input-box">
            <textarea
              value={input}
              onChange={(e) => setInput(e.target.value)}
              onKeyPress={handleKeyPress}
              placeholder={
                messages.length > 0 && 
                messages[messages.length - 1]?.content?.toLowerCase().includes('directory') &&
                messages[messages.length - 1]?.role === 'assistant'
                  ? "Enter absolute path (e.g., C:\\Users\\YourName\\Projects\\MyApp)"
                  : "Describe your coding task or bug... (Press Enter to send, Shift+Enter for new line)"
              }
              disabled={!isConnected || isSending}
              rows={1}
              onInput={(e) => {
                const target = e.target as HTMLTextAreaElement;
                target.style.height = 'auto';
                target.style.height = Math.min(target.scrollHeight, 200) + 'px';
              }}
            />
          </div>
          <button
            className="send-button"
            onClick={sendMessage}
            disabled={!input.trim() || !isConnected || isSending}
          >
            <span>{isSending ? 'Sending...' : 'Send'}</span>
            <span className="send-icon">
              {isSending ? '⏳' : '🚀'}
            </span>
          </button>
        </div>
      </div>
    </div>
  );
}

export default App;
