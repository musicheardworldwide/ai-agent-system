import React, { useState, useEffect, useRef } from 'react';
import { 
  Box, 
  Typography, 
  Paper, 
  TextField, 
  Button, 
  CircularProgress,
  Divider,
  List,
  ListItem,
  ListItemText,
  IconButton,
  Chip,
  Alert,
  Grid,
  Card,
  CardContent,
  CardActions
} from '@mui/material';
import SendIcon from '@mui/icons-material/Send';
import CodeIcon from '@mui/icons-material/Code';
import MemoryIcon from '@mui/icons-material/Memory';
import StorageIcon from '@mui/icons-material/Storage';
import BuildIcon from '@mui/icons-material/Build';
import { Prism as SyntaxHighlighter } from 'react-syntax-highlighter';
import { vscDarkPlus } from 'react-syntax-highlighter/dist/esm/styles/prism';

const Chat = () => {
  const [messages, setMessages] = useState([]);
  const [input, setInput] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [showMetadata, setShowMetadata] = useState(true);
  const messagesEndRef = useRef(null);
  const [streamingMessage, setStreamingMessage] = useState(null);

  useEffect(() => {
    // Load UI settings
    const loadSettings = async () => {
      try {
        const response = await fetch('/api/settings/ui');
        if (response.ok) {
          const data = await response.json();
          setShowMetadata(data.showMetadata);
        }
      } catch (error) {
        console.error('Error loading UI settings:', error);
      }
    };
    
    loadSettings();
    
    // Load chat history
    const loadChatHistory = async () => {
      try {
        const response = await fetch('/api/chat/history');
        if (response.ok) {
          const data = await response.json();
          setMessages(data.messages || []);
        }
      } catch (error) {
        console.error('Error loading chat history:', error);
      }
    };
    
    loadChatHistory();
  }, []);

  useEffect(() => {
    // Scroll to bottom when messages change
    scrollToBottom();
  }, [messages, streamingMessage]);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  const handleInputChange = (e) => {
    setInput(e.target.value);
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!input.trim()) return;
    
    // Add user message to chat
    const userMessage = {
      role: 'user',
      content: input,
      timestamp: new Date().toISOString()
    };
    
    setMessages(prev => [...prev, userMessage]);
    setInput('');
    setError(null);
    setLoading(true);
    
    try {
      // Check if streaming is supported
      const supportsStreaming = 'ReadableStream' in window && 'TextDecoderStream' in window;
      
      if (supportsStreaming) {
        // Use streaming for response
        await handleStreamingResponse(userMessage);
      } else {
        // Fallback to non-streaming
        await handleNonStreamingResponse(userMessage);
      }
    } catch (error) {
      console.error('Error sending message:', error);
      setError('Failed to send message. Please try again.');
      setLoading(false);
    }
  };

  const handleStreamingResponse = async (userMessage) => {
    try {
      const response = await fetch('/api/chat', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ 
          query: userMessage.content,
          stream: true
        }),
      });
      
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }
      
      const reader = response.body.getReader();
      const decoder = new TextDecoder();
      
      // Initialize streaming message
      setStreamingMessage({
        role: 'assistant',
        content: '',
        timestamp: new Date().toISOString(),
        metadata: {
          processing: true,
          tools: []
        }
      });
      
      let done = false;
      let buffer = '';
      
      while (!done) {
        const { value, done: doneReading } = await reader.read();
        done = doneReading;
        
        if (done) break;
        
        // Decode the chunk and add to buffer
        const chunk = decoder.decode(value, { stream: true });
        buffer += chunk;
        
        // Process complete JSON objects from buffer
        let startIdx = 0;
        let endIdx;
        
        while ((endIdx = buffer.indexOf('\n', startIdx)) !== -1) {
          const jsonStr = buffer.substring(startIdx, endIdx).trim();
          startIdx = endIdx + 1;
          
          if (jsonStr) {
            try {
              const data = JSON.parse(jsonStr);
              
              // Update streaming message
              setStreamingMessage(prev => {
                if (!prev) return null;
                
                const updatedMessage = { ...prev };
                
                if (data.type === 'content') {
                  updatedMessage.content += data.content;
                } else if (data.type === 'tool_start') {
                  updatedMessage.metadata.tools.push({
                    name: data.tool,
                    status: 'running',
                    input: data.input
                  });
                } else if (data.type === 'tool_end') {
                  const toolIndex = updatedMessage.metadata.tools.findIndex(t => 
                    t.name === data.tool && t.status === 'running');
                  
                  if (toolIndex !== -1) {
                    updatedMessage.metadata.tools[toolIndex].status = 'completed';
                    updatedMessage.metadata.tools[toolIndex].output = data.output;
                  }
                }
                
                return updatedMessage;
              });
            } catch (e) {
              console.error('Error parsing JSON:', e, jsonStr);
            }
          }
        }
        
        // Keep remaining partial data in buffer
        buffer = buffer.substring(startIdx);
      }
      
      // Finalize the message
      setStreamingMessage(prev => {
        if (!prev) return null;
        
        const finalMessage = { ...prev };
        finalMessage.metadata.processing = false;
        
        // Add to messages and clear streaming
        setMessages(messages => [...messages, finalMessage]);
        setStreamingMessage(null);
        
        return null;
      });
    } catch (error) {
      console.error('Error in streaming response:', error);
      setError('Failed to receive streaming response. Please try again.');
      setStreamingMessage(null);
    } finally {
      setLoading(false);
    }
  };

  const handleNonStreamingResponse = async (userMessage) => {
    try {
      const response = await fetch('/api/chat', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ 
          query: userMessage.content,
          stream: false
        }),
      });
      
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }
      
      const data = await response.json();
      
      // Add assistant message to chat
      setMessages(prev => [...prev, {
        role: 'assistant',
        content: data.response,
        timestamp: new Date().toISOString(),
        metadata: data.metadata || {}
      }]);
    } catch (error) {
      console.error('Error in non-streaming response:', error);
      setError('Failed to receive response. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  const renderMessageContent = (content) => {
    // Check for code blocks
    const codeBlockRegex = /```(\w+)?\n([\s\S]*?)```/g;
    const parts = [];
    let lastIndex = 0;
    let match;
    
    while ((match = codeBlockRegex.exec(content)) !== null) {
      // Add text before code block
      if (match.index > lastIndex) {
        parts.push({
          type: 'text',
          content: content.substring(lastIndex, match.index)
        });
      }
      
      // Add code block
      const language = match[1] || 'javascript';
      const code = match[2];
      parts.push({
        type: 'code',
        language,
        content: code
      });
      
      lastIndex = match.index + match[0].length;
    }
    
    // Add remaining text
    if (lastIndex < content.length) {
      parts.push({
        type: 'text',
        content: content.substring(lastIndex)
      });
    }
    
    // If no code blocks were found, return the content as is
    if (parts.length === 0) {
      return <Typography variant="body1" sx={{ whiteSpace: 'pre-wrap' }}>{content}</Typography>;
    }
    
    // Render parts
    return parts.map((part, index) => {
      if (part.type === 'text') {
        return (
          <Typography key={index} variant="body1" sx={{ whiteSpace: 'pre-wrap' }}>
            {part.content}
          </Typography>
        );
      } else if (part.type === 'code') {
        return (
          <Box key={index} sx={{ my: 2, position: 'relative' }}>
            <SyntaxHighlighter
              language={part.language}
              style={vscDarkPlus}
              customStyle={{ borderRadius: '4px' }}
            >
              {part.content}
            </SyntaxHighlighter>
            <Chip 
              label={part.language}
              size="small"
              sx={{ 
                position: 'absolute', 
                top: 0, 
                right: 0,
                borderTopLeftRadius: 0,
                borderBottomRightRadius: 0,
                backgroundColor: 'rgba(0,0,0,0.6)',
                color: 'white'
              }}
            />
          </Box>
        );
      }
      return null;
    });
  };

  const renderToolMetadata = (tools) => {
    if (!tools || tools.length === 0) return null;
    
    return (
      <Box sx={{ mt: 2 }}>
        <Typography variant="subtitle2" color="text.secondary">
          Tools Used:
        </Typography>
        <List dense sx={{ bgcolor: 'background.paper', borderRadius: 1 }}>
          {tools.map((tool, index) => (
            <ListItem key={index} sx={{ py: 0 }}>
              <ListItemText
                primary={
                  <Box sx={{ display: 'flex', alignItems: 'center' }}>
                    <BuildIcon fontSize="small" sx={{ mr: 1 }} />
                    <Typography variant="body2" component="span" fontWeight="bold">
                      {tool.name}
                    </Typography>
                    <Chip
                      label={tool.status}
                      size="small"
                      color={tool.status === 'completed' ? 'success' : 'warning'}
                      sx={{ ml: 1, height: 20 }}
                    />
                  </Box>
                }
                secondary={
                  <Box sx={{ mt: 1 }}>
                    {tool.input && (
                      <Typography variant="caption" component="div" sx={{ mb: 0.5 }}>
                        Input: {JSON.stringify(tool.input)}
                      </Typography>
                    )}
                    {tool.output && (
                      <Typography variant="caption" component="div">
                        Output: {typeof tool.output === 'object' 
                          ? JSON.stringify(tool.output) 
                          : tool.output}
                      </Typography>
                    )}
                  </Box>
                }
              />
            </ListItem>
          ))}
        </List>
      </Box>
    );
  };

  const renderMessage = (message, index) => {
    const isUser = message.role === 'user';
    const formattedTime = new Date(message.timestamp).toLocaleTimeString();
    
    return (
      <Box
        key={index}
        sx={{
          display: 'flex',
          flexDirection: 'column',
          alignItems: isUser ? 'flex-end' : 'flex-start',
          mb: 2,
          maxWidth: '100%'
        }}
      >
        <Paper
          elevation={1}
          sx={{
            p: 2,
            borderRadius: 2,
            maxWidth: '80%',
            bgcolor: isUser ? 'primary.light' : 'background.paper',
            color: isUser ? 'primary.contrastText' : 'text.primary'
          }}
        >
          {renderMessageContent(message.content)}
          
          {!isUser && showMetadata && message.metadata && (
            <>
              {message.metadata.processing && (
                <Box sx={{ display: 'flex', alignItems: 'center', mt: 2 }}>
                  <CircularProgress size={16} sx={{ mr: 1 }} />
                  <Typography variant="caption">Processing...</Typography>
                </Box>
              )}
              
              {message.metadata.tools && renderToolMetadata(message.metadata.tools)}
              
              {message.metadata.sources && (
                <Box sx={{ mt: 2 }}>
                  <Typography variant="subtitle2" color="text.secondary">
                    Sources:
                  </Typography>
                  <List dense>
                    {message.metadata.sources.map((source, idx) => (
                      <ListItem key={idx} sx={{ py: 0 }}>
                        <ListItemText
                          primary={source.title}
                          secondary={source.url}
                        />
                      </ListItem>
                    ))}
                  </List>
                </Box>
              )}
            </>
          )}
        </Paper>
        
        <Typography variant="caption" color="text.secondary" sx={{ mt: 0.5 }}>
          {isUser ? 'You' : 'AI'} • {formattedTime}
        </Typography>
      </Box>
    );
  };

  return (
    <Box sx={{ height: '100%', display: 'flex', flexDirection: 'column' }}>
      <Typography variant="h4" component="h1" gutterBottom>
        Chat
      </Typography>
      
      {error && (
        <Alert severity="error" sx={{ mb: 2 }} onClose={() => setError(null)}>
          {error}
        </Alert>
      )}
      
      <Paper 
        elevation={3} 
        sx={{ 
          p: 2, 
          flexGrow: 1, 
          mb: 2, 
          display: 'flex', 
          flexDirection: 'column',
          height: 'calc(100vh - 220px)',
          maxHeight: 'calc(100vh - 220px)'
        }}
      >
        <Box sx={{ 
          flexGrow: 1, 
          overflowY: 'auto', 
          mb: 2,
          p: 1
        }}>
          {messages.length === 0 ? (
            <Box sx={{ 
              height: '100%', 
              display: 'flex', 
              flexDirection: 'column', 
              justifyContent: 'center', 
              alignItems: 'center',
              color: 'text.secondary'
            }}>
              <Typography variant="h6" gutterBottom>
                Welcome to AI Agent System
              </Typography>
              
              <Typography variant="body2" sx={{ mb: 4, textAlign: 'center' }}>
                Start a conversation or try one of the example queries below
              </Typography>
              
              <Grid container spacing={2} sx={{ maxWidth: 800 }}>
                <Grid item xs={12} sm={6} md={4}>
                  <Card variant="outlined">
                    <CardContent>
                      <Box sx={{ display: 'flex', mb: 1 }}>
                        <CodeIcon color="primary" sx={{ mr: 1 }} />
                        <Typography variant="subtitle1">Code Execution</Typography>
                      </Box>
                      <Typography variant="body2">
                        "Write a Python function to calculate the Fibonacci sequence"
                      </Typography>
                    </CardContent>
                    <CardActions>
                      <Button 
                        size="small" 
                        onClick={() => setInput("Write a Python function to calculate the Fibonacci sequence")}
                      >
                        Try this
                      </Button>
                    </CardActions>
                  </Card>
                </Grid>
                
                <Grid item xs={12} sm={6} md={4}>
                  <Card variant="outlined">
                    <CardContent>
                      <Box sx={{ display: 'flex', mb: 1 }}>
                        <MemoryIcon color="primary" sx={{ mr: 1 }} />
                        <Typography variant="subtitle1">Memory System</Typography>
                      </Box>
                      <Typography variant="body2">
                        "Remember that my favorite color is blue"
                      </Typography>
                    </CardContent>
                    <CardActions>
                      <Button 
                        size="small" 
                        onClick={() => setInput("Remember that my favorite color is blue")}
                      >
                        Try this
                      </Button>
                    </CardActions>
                  </Card>
                </Grid>
                
                <Grid item xs={12} sm={6} md={4}>
                  <Card variant="outlined">
                    <CardContent>
                      <Box sx={{ display: 'flex', mb: 1 }}>
                        <StorageIcon color="primary" sx={{ mr: 1 }} />
                        <Typography variant="subtitle1">Database Agent</Typography>
                      </Box>
                      <Typography variant="body2">
                        "Create a knowledge entry about quantum computing"
                      </Typography>
                    </CardContent>
                    <CardActions>
                      <Button 
                        size="small" 
                        onClick={() => setInput("Create a knowledge entry about quantum computing")}
                      >
                        Try this
                      </Button>
                    </CardActions>
                  </Card>
                </Grid>
              </Grid>
            </Box>
          ) : (
            <>
              {messages.map(renderMessage)}
              {streamingMessage && renderMessage(streamingMessage, 'streaming')}
              <div ref={messagesEndRef} />
            </>
          )}
        </Box>
        
        <Divider />
        
        <Box component="form" onSubmit={handleSubmit} sx={{ mt: 2, display: 'flex' }}>
          <TextField
            fullWidth
            placeholder="Type your message..."
            value={input}
            onChange={handleInputChange}
            variant="outlined"
            disabled={loading}
            multiline
            maxRows={4}
            sx={{ mr: 1 }}
          />
          <Button
            type="submit"
            variant="contained"
            color="primary"
            disabled={loading || !input.trim()}
            endIcon={loading ? <CircularProgress size={24} /> : <SendIcon />}
          >
            Send
          </Button>
        </Box>
      </Paper>
    </Box>
  );
};

export default Chat;
