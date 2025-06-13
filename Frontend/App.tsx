import React, { useState, useRef, useEffect } from 'react';
import axios from 'axios';
import { Send, User, Bot } from 'lucide-react';
import './App.css';

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
  const socket = useRef<WebSocket | null>(null);
  const useWebSocket = useRef(true); // ✅ Flag to toggle mode
  const messagesEndRef = useRef<HTMLDivElement>(null);

  // ✅ Scroll to latest message
  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  // ✅ Setup WebSocket once
  useEffect(() => {
    socket.current = new WebSocket('ws://localhost:8000/ws/chat');

    socket.current.onopen = () => {
      console.log('✅ WebSocket connected');
      useWebSocket.current = true;
    };

    socket.current.onmessage = (event) => {
      if (event.data === 'typing...') {
        setIsTyping(true);
      } else {
        setIsTyping(false);
        const botMessage: Message = {
          id: Date.now().toString() + '-bot',
          type: 'bot',
          content: event.data,
          timestamp: new Date(),
        };
        setMessages((prev) => [...prev, botMessage]);
      }
    };

    socket.current.onerror = () => {
      console.error('❌ WebSocket error. Falling back to Axios.');
      useWebSocket.current = false;
    };

    socket.current.onclose = () => {
      console.log('❌ WebSocket disconnected. Using Axios fallback.');
      useWebSocket.current = false;
    };

    return () => {
      socket.current?.close();
    };
  }, []);

  // ✅ Handle message send
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
      if (useWebSocket.current && socket.current?.readyState === WebSocket.OPEN) {
        socket.current.send(inputValue);
      } else {
        // ✅ Fallback: Axios POST
        const response = await axios.post(
          'http://127.0.0.1:8000/chat',
          { query: userMessage.content },
          {
            headers: { 'Content-Type': 'application/json' },
          }
        );

        const botReply = response.data || "🤖 Sorry, I didn't understand that.";

        const botMessage: Message = {
          id: Date.now().toString() + '-bot',
          type: 'bot',
          content: botReply,
          timestamp: new Date(),
        };

        setMessages((prev) => [...prev, botMessage]);
      }
    } catch (error: any) {
      const errorMsg = error?.response?.data?.detail || error.message || 'Unknown error';
      setMessages((prev) => [
        ...prev,
        {
          id: Date.now().toString() + '-error',
          type: 'bot',
          content: `❌ Error: ${errorMsg}`,
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
        <span className="status">{useWebSocket.current ? 'Live' : 'Fallback'}</span>
      </div>

      <div className="chat-body">
        {messages.map((msg) => (
          <div key={msg.id} className={`message ${msg.type}`}>
            <div className="message-icon">{msg.type === 'user' ? <User /> : <Bot />}</div>
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
