import { useState } from 'react';
import ReactMarkdown from 'react-markdown';

const INTENT_LABELS = {
  customer_query: '👤 Customer Query',
  product_query: '📦 Product Query',
  business_metric: '📊 Business Metric',
  comparison: '⚖️ Comparison',
  general: '💬 General',
};

function MessageBubble({ role, content, sourceData, intent }) {
  const [showSource, setShowSource] = useState(false);

  const hasSource = role === 'assistant' && sourceData && 
    sourceData !== 'No specific data retrieval needed for this query.';

  return (
    <div className={`message ${role}`}>
      <div className={`message-bubble ${role}-bubble`}>
        {role === 'assistant' ? (
          <div className="markdown-content">
            <ReactMarkdown>{content}</ReactMarkdown>
          </div>
        ) : (
          <p>{content}</p>
        )}

        {hasSource && (
          <div className="source-section">
            <button
              className="source-toggle"
              onClick={() => setShowSource(!showSource)}
            >
              <span className="source-icon">📋</span>
              <span>{showSource ? 'Hide' : 'View'} Source Data</span>
              {intent && (
                <span className="intent-badge">
                  {INTENT_LABELS[intent] || intent}
                </span>
              )}
              <span className={`source-chevron ${showSource ? 'open' : ''}`}>▾</span>
            </button>

            {showSource && (
              <pre className="source-data">{sourceData}</pre>
            )}
          </div>
        )}
      </div>
    </div>
  );
}

export default MessageBubble;
