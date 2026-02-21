import { useState } from 'react';
import './index.css';
import ChatWindow from './components/ChatWindow';
import ChatInput from './components/ChatInput';
import { sendMessage } from './services/api';

function App() {
  const SUGGESTIONS = [
    'What has customer 109318 purchased?',
    'Which stores sell product A?',
    'What is the total revenue by category?',
    'Compare product A vs product B',
  ];

  const [messages, setMessages] = useState([
    {
      role: 'assistant',
      content: 'Hello! I can help you analyze retail transaction data. Try one of these:',
      suggestions: SUGGESTIONS,
    },
  ]);
  const [loading, setLoading] = useState(false);

  const handleSend = async (text) => {
    if (!text.trim() || loading) return;

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
          chartData: data.chart_data,
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
            <h1>Retail Analytics Chat</h1>
          </div>
          <p className="subtitle">AI-powered insights from your transaction data</p>
        </div>
      </header>
      <main className="chat-container">
        <ChatWindow messages={messages} loading={loading} onSuggestionClick={handleSend} />
        <ChatInput onSend={handleSend} disabled={loading} />
      </main>
    </div>
  );
}

export default App;
