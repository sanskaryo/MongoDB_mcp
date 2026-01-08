import React, { useState, useRef, useEffect } from 'react';
import ReactMarkdown from 'react-markdown';
import remarkGfm from 'remark-gfm';
import './App.css';

function App() {
  const [messages, setMessages] = useState([]);
  const [inputText, setInputText] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [tools, setTools] = useState([]);
  const [showTools, setShowTools] = useState(false);
  const messagesEndRef = useRef(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  // Fetch available tools
  useEffect(() => {
    fetchTools();
  }, []);

  const fetchTools = async () => {
    try {
      const response = await fetch('http://localhost:8001/tools');
      if (response.ok) {
        const data = await response.json();
        setTools(data.tools || []);
      }
    } catch (error) {
      console.error('Failed to fetch tools:', error);
    }
  };

  const sendMessage = async (text) => {
    if (!text.trim()) return;

    const userMessage = { role: 'user', content: text };
    setMessages(prev => [...prev, userMessage]);
    setInputText('');
    setIsLoading(true);

    try {
      const response = await fetch('http://localhost:8001/query', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          query: text,
          generate_chart: false
        }),
      });

      if (response.ok) {
        const data = await response.json();
        if (data.success) {
          let messageContent = data.response;

          const assistantMessage = {
            role: 'assistant',
            content: messageContent,
            chart_path: data.chart_path,
            chart_title: data.chart_title
          };
          setMessages(prev => [...prev, assistantMessage]);
        } else {
          const errorMessage = {
            role: 'assistant',
            content: data.error || 'An error occurred while processing your request.'
          };
          setMessages(prev => [...prev, errorMessage]);
        }
      } else {
        throw new Error(`Server responded with status: ${response.status}`);
      }
    } catch (error) {
      console.error('Error:', error);
      const errorMessage = {
        role: 'assistant',
        content: 'Sorry, I encountered an error while processing your request. Please make sure the backend server is running on port 8001.'
      };
      setMessages(prev => [...prev, errorMessage]);
    } finally {
      setIsLoading(false);
    }
  };

  const handleSubmit = (e) => {
    e.preventDefault();
    sendMessage(inputText);
  };

  const handleExampleClick = (exampleText) => {
    sendMessage(exampleText);
  };

  const startNewChat = () => {
    setMessages([]);
  };

  return (
    <div className="app">
      {/* Header */}
      <div className="header">
        <div className="header-content">
          <div className="logo">
            <span className="logo-icon">🏨</span>
            <h1>X-Hotel Analytics - MCP Agent</h1>
          </div>
          <div className="header-actions">
            <button
              className={`tools-toggle ${showTools ? 'active' : ''}`}
              onClick={() => setShowTools(!showTools)}
            >
              🛠️ Tools ({tools.length})
            </button>
          </div>
        </div>
      </div>

      <div className="main-content">
        {/* Sidebar */}
        <div className="sidebar">
          <div className="sidebar-header">
            <button className="new-chat-btn" onClick={startNewChat}>
              <span className="plus-icon">+</span>
              New Analysis
            </button>
          </div>

          {/* Tools Panel */}
          {showTools && (
            <div className="tools-panel">
              <h3>Available Tools</h3>
              <div className="tools-list">
                {tools.map((tool, index) => (
                  <div key={index} className="tool-item">
                    <div className="tool-name">{tool.name}</div>
                    <div className="tool-description">{tool.description}</div>
                    {tool.parameters && tool.parameters.length > 0 && (
                      <div className="tool-params">
                        <small>Parameters: {tool.parameters.join(', ')}</small>
                      </div>
                    )}
                  </div>
                ))}
              </div>
            </div>
          )}

          <div className="sidebar-footer">
            <div className="status-indicator">
              <span className="status-dot"></span>
              <span>Connected to MongoDB</span>
            </div>
          </div>
        </div>

        {/* Main Chat Area */}
        <div className="chat-area">
          {messages.length === 0 ? (
            <div className="welcome-screen">
              <div className="welcome-content">
                <div className="welcome-header">
                  <div className="welcome-icon">📊</div>
                  <h2>Welcome to X-Hotel Analytics</h2>
                  <p>Powered by MongoDB MCP Agent - Your intelligent data analysis companion</p>
                </div>

                <div className="examples-grid">
                  <div
                    className="example-card"
                    onClick={() => handleExampleClick("Show me today's revenue breakdown")}
                  >
                    <div className="example-icon">💰</div>
                    <div className="example-content">
                      <h4>Revenue Analytics</h4>
                      <p>Show me today's revenue breakdown</p>
                    </div>
                  </div>

                  <div
                    className="example-card"
                    onClick={() => handleExampleClick("What are the most popular menu items this month?")}
                  >
                    <div className="example-icon">🍽️</div>
                    <div className="example-content">
                      <h4>Menu Performance</h4>
                      <p>What are the most popular menu items this month?</p>
                    </div>
                  </div>

                  <div
                    className="example-card"
                    onClick={() => handleExampleClick("Show a pie chart for revenue split across dine in and delivery methods")}
                  >
                    <div className="example-icon">📈</div>
                    <div className="example-content">
                      <h4>Data Visualization</h4>
                      <p>Show pie chart for revenue split by order type</p>
                    </div>
                  </div>

                  <div
                    className="example-card"
                    onClick={() => handleExampleClick("Analyze customer segments and their spending patterns")}
                  >
                    <div className="example-icon">👥</div>
                    <div className="example-content">
                      <h4>Customer Insights</h4>
                      <p>Analyze customer segments and their spending patterns</p>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          ) : (
            <div className="chat-container">
              <div className="messages">
                {messages.map((message, index) => (
                  <div key={index} className={`message ${message.role}`}>
                    <div className="message-avatar">
                      {message.role === 'user' ? '👤' : '🤖'}
                    </div>
                    <div className="message-content">
                      <div className="message-text">
                        <ReactMarkdown
                          remarkPlugins={[remarkGfm]}
                          components={{
                            img: ({ node, ...props }) => (
                              <div className="chart-container">
                                <img
                                  {...props}
                                  className="chart-image"
                                  style={{
                                    maxWidth: '100%',
                                    height: 'auto',
                                    borderRadius: '8px',
                                    marginTop: '12px',
                                    border: '1px solid #e5e5e7'
                                  }}
                                  alt={props.alt || "Chart"}
                                />
                              </div>
                            ),
                            table: ({ node, ...props }) => (
                              <div className="table-container">
                                <table className="markdown-table" {...props} />
                              </div>
                            )
                          }}
                        >
                          {message.content}
                        </ReactMarkdown>
                      </div>

                      {/* Display chart if available */}
                      {message.chart_path && (
                        <div className="chart-container">
                          <img
                            src={`http://localhost:8001${message.chart_path}`}
                            alt={message.chart_title || "Generated Chart"}
                            className="chart-image"
                            style={{
                              maxWidth: '100%',
                              height: 'auto',
                              borderRadius: '12px',
                              marginTop: '16px',
                              border: '2px solid #e5e5e7',
                              boxShadow: '0 4px 12px rgba(0,0,0,0.1)'
                            }}
                            onError={(e) => {
                              console.error('Failed to load chart:', message.chart_path);
                              e.target.style.display = 'none';
                            }}
                          />
                          {message.chart_title && (
                            <div style={{
                              fontSize: '13px',
                              color: '#666',
                              marginTop: '8px',
                              textAlign: 'center',
                              fontWeight: '500'
                            }}>
                              📊 {message.chart_title}
                            </div>
                          )}
                        </div>
                      )}

                      <div className="message-time">
                        {new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
                      </div>
                    </div>
                  </div>
                ))}
                {isLoading && (
                  <div className="message assistant">
                    <div className="message-avatar">🤖</div>
                    <div className="message-content">
                      <div className="typing-indicator">
                        <span></span>
                        <span></span>
                        <span></span>
                      </div>
                    </div>
                  </div>
                )}
                <div ref={messagesEndRef} />
              </div>
            </div>
          )}

          <div className="input-area">
            <div className="input-container">
              <form onSubmit={handleSubmit} className="input-form">
                <div className="input-wrapper">
                  <input
                    type="text"
                    value={inputText}
                    onChange={(e) => setInputText(e.target.value)}
                    placeholder="Ask about hotel analytics, revenue, orders, customers..."
                    className="chat-input"
                    disabled={isLoading}
                  />
                  <button
                    type="submit"
                    disabled={!inputText.trim() || isLoading}
                    className="send-button"
                  >
                    <svg width="16" height="16" viewBox="0 0 16 16" fill="none">
                      <path d="M.5 1.163A1 1 0 0 1 1.97.28l12.868 6.837a1 1 0 0 1 0 1.766L1.969 15.72A1 1 0 0 1 .5 14.836V10.33a1 1 0 0 1 .816-.983L8.5 8 1.316 6.653A1 1 0 0 1 .5 5.67V1.163Z" fill="currentColor" />
                    </svg>
                  </button>
                </div>
              </form>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}

export default App;