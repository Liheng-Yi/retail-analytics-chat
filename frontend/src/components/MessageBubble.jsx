function MessageBubble({ role, content }) {
  return (
    <div className={`message ${role}`}>
      <div className={`message-bubble ${role}-bubble`}>
        <p style={{ whiteSpace: 'pre-wrap' }}>{content}</p>
      </div>
    </div>
  );
}

export default MessageBubble;
