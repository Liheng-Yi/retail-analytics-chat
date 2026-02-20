import { useEffect, useRef } from 'react';
import MessageBubble from './MessageBubble';

function ChatWindow({ messages, loading }) {
  const bottomRef = useRef(null);

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages, loading]);

  return (
    <div className="chat-window">
      {messages.map((msg, i) => (
        <MessageBubble
          key={i}
          role={msg.role}
          content={msg.content}
          sourceData={msg.sourceData}
          intent={msg.intent}
        />
      ))}
      {loading && (
        <div className="message assistant">
          <div className="message-bubble assistant-bubble">
            <div className="typing-indicator">
              <span></span><span></span><span></span>
            </div>
          </div>
        </div>
      )}
      <div ref={bottomRef} />
    </div>
  );
}

export default ChatWindow;
