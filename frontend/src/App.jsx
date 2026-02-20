import { useState } from 'react';
import './index.css';
import ChatWindow from './components/ChatWindow';
import ChatInput from './components/ChatInput';
import { sendMessage } from './services/api';

function App() {
  const [messages, setMessages] = useState([
    {
      role: 'assistant',
      content: 'Hello! I can help you analyze retail transaction data. Try asking about a customer or product — for example:\n\n• "What has customer 109318 purchased?"\n• "Which stores sell product A?"\n• "What is the total revenue by category?"',
    },
  ]);
  const [loading, setLoading] = useState(false);

  const handleSend = async (text) => {
    if (!text.trim()) return;

    const userMsg = { role: 'user', content: text };
    setMessages((prev) => [...prev, userMsg]);
    setLoading(true);

    try {
      const data = await sendMessage(text);
      setMessages((prev) => [
        ...prev,
        {
          role: 'assistant',
          content: data.response,
          sourceData: data.source_data,
          intent: data.intent,
        },
      ]);
    } catch {
      setMessages((prev) => [
        ...prev,
        { role: 'assistant', content: 'Sorry, something went wrong. Please try again.' },
      ]);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="app">
      <header className="app-header">
        <div className="header-content">
          <div className="logo">
            <span className="logo-icon">📊</span>
            <h1>Retail Analytics Chat</h1>
          </div>
          <p className="subtitle">AI-powered insights from your transaction data</p>
        </div>
      </header>
      <main className="chat-container">
        <ChatWindow messages={messages} loading={loading} />
        <ChatInput onSend={handleSend} disabled={loading} />
      </main>
    </div>
  );
}

export default App;
