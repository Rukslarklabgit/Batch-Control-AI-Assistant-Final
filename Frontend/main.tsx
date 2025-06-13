import { useState, useRef, useEffect } from 'react';
import axios from 'axios';
import { Send, User, Bot } from 'lucide-react';
import './App.css';

import React from 'react';
import ReactDOM from 'react-dom/client';
// import ChatInterface from './App.tsx'; // Removed to avoid naming conflict
import './index.css';              // ✅ Optional: keep if you have custom styles

ReactDOM.createRoot(document.getElementById('root')!).render(
  <React.StrictMode>
    
  </React.StrictMode>
);


type Message = {
  id: string;
  type: 'user' | 'bot';
  content: string;
  timestamp: Date;
};

const ChatInterface = () => {
  const [messages, setMessages] = useState<Message[]>([
    {
      id: '1',
      type: 'bot',
      content: 'Hello! How can I help you today?',
      timestamp: new Date(),
    },
  ]);

  const [inputValue, setInputValue] = useState('');
  const [isTyping, setIsTyping] = useState(false);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const handleSend = async () => {
    if (!inputValue.trim()) return;

    const userMessage: Message = {
      id: Date.now().toString(),
      type: 'user',
      content: inputValue,
      timestamp: new Date(),
    };

    setMessages((prev) => [...prev, userMessage]);
    setInputValue('');
    setIsTyping(true);
try {
  const response = await axios.post(
  'http://127.0.0.1:8000/chat',
  { message: userMessage.content }, // ✅ Correct structure
  {
    headers: {
      'Content-Type': 'application/json'
    }
  }
);


      let botReply = '';

      if (response.data?.result?.length) {
        botReply = JSON.stringify(response.data.result[0], null, 2);
      } else if (response.data?.query) {
        botReply = `You said: "${userMessage.content}". Here's the SQL:\n${response.data.query}`;
      } else if (response.data?.error) {
        botReply = `⚠️ Error: ${response.data.error}`;
      } else {
        botReply = `You said: "${userMessage.content}". In a real implementation, this would connect to your backend API.`;
      }

      const botMessage: Message = {
        id: Date.now().toString() + '-bot',
        type: 'bot',
        content: botReply,
        timestamp: new Date(),
      };

      setMessages((prev) => [...prev, botMessage]);
    } catch (error: any) {
      setMessages((prev) => [
        ...prev,
        {
          id: Date.now().toString() + '-bot-error',
          type: 'bot',
          content: `⚠️ Failed to fetch response: ${error.message}`,
          timestamp: new Date(),
        },
      ]);
    } finally {
      setIsTyping(false);
    }
  };

  return (
    <div className="chat-container">
      <div className="chat-header">
        <Bot className="icon" />
        <h2>AI Assistant</h2>
        <span className="status">Online</span>
      </div>

      <div className="chat-body">
        {messages.map((msg) => (
          <div key={msg.id} className={`message ${msg.type}`}>
            <div className="message-icon">
              {msg.type === 'user' ? <User /> : <Bot />}
            </div>
            <div className="message-content">
              {msg.content.split('\n').map((line, idx) => (
                <pre key={idx}>{line}</pre>
              ))}
            </div>
          </div>
        ))}
        {isTyping && <div className="typing-indicator">Assistant is typing...</div>}
        <div ref={messagesEndRef} />
      </div>

      <div className="chat-input">
        <input
          type="text"
          placeholder="Type your message..."
          value={inputValue}
          onChange={(e) => setInputValue(e.target.value)}
          onKeyDown={(e) => e.key === 'Enter' && handleSend()}
        />
        <button onClick={handleSend}>
          <Send />
        </button>
      </div>
    </div>
  );
};

export default ChatInterface;

