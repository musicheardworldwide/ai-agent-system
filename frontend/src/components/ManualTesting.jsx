import React, { useState, useEffect } from 'react';
import { 
  Box, 
  Typography, 
  Paper, 
  Tabs, 
  Tab, 
  Button, 
  CircularProgress, 
  Alert,
  Grid,
  Card,
  CardContent,
  CardActions,
  Divider,
  List,
  ListItem,
  ListItemText,
  ListItemIcon,
  TextField,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions
} from '@mui/material';
import PlayArrowIcon from '@mui/icons-material/PlayArrow';
import CheckCircleIcon from '@mui/icons-material/CheckCircle';
import ErrorIcon from '@mui/icons-material/Error';
import WarningIcon from '@mui/icons-material/Warning';
import InfoIcon from '@mui/icons-material/Info';
import RefreshIcon from '@mui/icons-material/Refresh';
import TerminalIcon from '@mui/icons-material/Terminal';
import StorageIcon from '@mui/icons-material/Storage';
import MemoryIcon from '@mui/icons-material/Memory';
import BuildIcon from '@mui/icons-material/Build';
import CodeIcon from '@mui/icons-material/Code';
import VpnKeyIcon from '@mui/icons-material/VpnKey';
import BugReportIcon from '@mui/icons-material/BugReport';
import SendIcon from '@mui/icons-material/Send';
import { Prism as SyntaxHighlighter } from 'react-syntax-highlighter';
import { vscDarkPlus } from 'react-syntax-highlighter/dist/esm/styles/prism';

const ManualTesting = () => {
  const [activeTab, setActiveTab] = useState(0);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [chatInput, setChatInput] = useState('');
  const [chatMessages, setChatMessages] = useState([]);
  const [chatLoading, setChatLoading] = useState(false);
  const [dbQuery, setDbQuery] = useState('');
  const [dbResult, setDbResult] = useState(null);
  const [dbLoading, setDbLoading] = useState(false);
  const [ragQuery, setRagQuery] = useState('');
  const [ragResult, setRagResult] = useState(null);
  const [ragLoading, setRagLoading] = useState(false);
  const [toolName, setToolName] = useState('');
  const [toolParams, setToolParams] = useState('{}');
  const [toolResult, setToolResult] = useState(null);
  const [toolLoading, setToolLoading] = useState(false);
  const [envKey, setEnvKey] = useState('');
  const [envValue, setEnvValue] = useState('');
  const [envResult, setEnvResult] = useState(null);
  const [envLoading, setEnvLoading] = useState(false);
  const [devChatQuery, setDevChatQuery] = useState('');
  const [devChatResult, setDevChatResult] = useState(null);
  const [devChatLoading, setDevChatLoading] = useState(false);
  const [openScreenshotDialog, setOpenScreenshotDialog] = useState(false);
  const [screenshotData, setScreenshotData] = useState(null);
  const [testLogs, setTestLogs] = useState([]);

  useEffect(() => {
    // Load any existing test logs
    const loadTestLogs = async () => {
      try {
        const response = await fetch('/api/tests/manual/logs');
        if (response.ok) {
          const data = await response.json();
          if (data.logs) {
            setTestLogs(data.logs);
          }
        }
      } catch (error) {
        console.error('Error loading test logs:', error);
      }
    };
    
    loadTestLogs();
  }, []);

  const handleTabChange = (event, newValue) => {
    setActiveTab(newValue);
  };

  const addTestLog = (component, action, result, status) => {
    const newLog = {
      timestamp: new Date().toISOString(),
      component,
      action,
      result,
      status
    };
    
    setTestLogs(prev => [newLog, ...prev]);
    
    // Save log to server
    try {
      fetch('/api/tests/manual/log', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(newLog),
      });
    } catch (error) {
      console.error('Error saving test log:', error);
    }
  };

  const handleChatSubmit = async (e) => {
    e.preventDefault();
    if (!chatInput.trim()) return;
    
    const userMessage = {
      role: 'user',
      content: chatInput,
      timestamp: new Date().toISOString()
    };
    
    setChatMessages(prev => [...prev, userMessage]);
    setChatInput('');
    setChatLoading(true);
    
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
      const assistantMessage = {
        role: 'assistant',
        content: data.response,
        timestamp: new Date().toISOString(),
        metadata: data.metadata || {}
      };
      
      setChatMessages(prev => [...prev, assistantMessage]);
      
      // Log the test
      addTestLog(
        'Chat Agent', 
        `Query: "${userMessage.content.substring(0, 30)}${userMessage.content.length > 30 ? '...' : ''}"`, 
        `Response received (${data.response.length} chars)`, 
        'success'
      );
      
    } catch (error) {
      console.error('Error sending message:', error);
      setError('Failed to send message. Please try again.');
      
      // Log the test failure
      addTestLog(
        'Chat Agent', 
        `Query: "${chatInput.substring(0, 30)}${chatInput.length > 30 ? '...' : ''}"`, 
        `Error: ${error.message}`, 
        'error'
      );
      
    } finally {
      setChatLoading(false);
    }
  };

  const handleDbQuery = async () => {
    if (!dbQuery.trim()) return;
    
    setDbLoading(true);
    setDbResult(null);
    
    try {
      const response = await fetch('/api/database/query', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ query: dbQuery }),
      });
      
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }
      
      const data = await response.json();
      setDbResult(data);
      
      // Log the test
      addTestLog(
        'Database Agent', 
        `Query: "${dbQuery.substring(0, 30)}${dbQuery.length > 30 ? '...' : ''}"`, 
        `Results: ${data.results ? data.results.length : 0} entries found`, 
        'success'
      );
      
    } catch (error) {
      console.error('Error querying database:', error);
      setError('Failed to query database. Please try again.');
      setDbResult({ error: error.message });
      
      // Log the test failure
      addTestLog(
        'Database Agent', 
        `Query: "${dbQuery.substring(0, 30)}${dbQuery.length > 30 ? '...' : ''}"`, 
        `Error: ${error.message}`, 
        'error'
      );
      
    } finally {
      setDbLoading(false);
    }
  };

  const handleRagQuery = async () => {
    if (!ragQuery.trim()) return;
    
    setRagLoading(true);
    setRagResult(null);
    
    try {
      const response = await fetch('/api/rag/retrieve', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ query: ragQuery }),
      });
      
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }
      
      const data = await response.json();
      setRagResult(data);
      
      // Log the test
      addTestLog(
        'RAG Memory', 
        `Query: "${ragQuery.substring(0, 30)}${ragQuery.length > 30 ? '...' : ''}"`, 
        `Retrieved ${data.memories ? data.memories.length : 0} memories`, 
        'success'
      );
      
    } catch (error) {
      console.error('Error querying RAG memory:', error);
      setError('Failed to query RAG memory. Please try again.');
      setRagResult({ error: error.message });
      
      // Log the test failure
      addTestLog(
        'RAG Memory', 
        `Query: "${ragQuery.substring(0, 30)}${ragQuery.length > 30 ? '...' : ''}"`, 
        `Error: ${error.message}`, 
        'error'
      );
      
    } finally {
      setRagLoading(false);
    }
  };

  const handleToolExecution = async () => {
    if (!toolName.trim()) return;
    
    let parsedParams;
    try {
      parsedParams = JSON.parse(toolParams);
    } catch (e) {
      setError('Invalid JSON in tool parameters');
      return;
    }
    
    setToolLoading(true);
    setToolResult(null);
    
    try {
      const response = await fetch('/api/tools/execute', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ 
          name: toolName,
          parameters: parsedParams
        }),
      });
      
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }
      
      const data = await response.json();
      setToolResult(data);
      
      // Log the test
      addTestLog(
        'Custom Tools', 
        `Execute: "${toolName}" with params ${JSON.stringify(parsedParams).substring(0, 30)}...`, 
        `Tool executed successfully`, 
        'success'
      );
      
    } catch (error) {
      console.error('Error executing tool:', error);
      setError('Failed to execute tool. Please try again.');
      setToolResult({ error: error.message });
      
      // Log the test failure
      addTestLog(
        'Custom Tools', 
        `Execute: "${toolName}" with params ${JSON.stringify(parsedParams).substring(0, 30)}...`, 
        `Error: ${error.message}`, 
        'error'
      );
      
    } finally {
      setToolLoading(false);
    }
  };

  const handleEnvOperation = async (operation) => {
    if (!envKey.trim()) return;
    
    setEnvLoading(true);
    setEnvResult(null);
    
    try {
      let url, body;
      
      switch (operation) {
        case 'get':
          url = `/api/env/${envKey}`;
          body = null;
          break;
        case 'set':
          url = '/api/env/set';
          body = JSON.stringify({ key: envKey, value: envValue });
          break;
        case 'delete':
          url = '/api/env/delete';
          body = JSON.stringify({ key: envKey });
          break;
        default:
          throw new Error('Invalid operation');
      }
      
      const response = await fetch(url, {
        method: body ? 'POST' : 'GET',
        headers: body ? {
          'Content-Type': 'application/json',
        } : undefined,
        body,
      });
      
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }
      
      const data = await response.json();
      setEnvResult(data);
      
      // Log the test
      addTestLog(
        'Environment Manager', 
        `${operation.charAt(0).toUpperCase() + operation.slice(1)}: "${envKey}"${operation === 'set' ? ` = "${envValue}"` : ''}`, 
        `Operation completed successfully`, 
        'success'
      );
      
    } catch (error) {
      console.error('Error with environment variable:', error);
      setError(`Failed to ${operation} environment variable. Please try again.`);
      setEnvResult({ error: error.message });
      
      // Log the test failure
      addTestLog(
        'Environment Manager', 
        `${operation.charAt(0).toUpperCase() + operation.slice(1)}: "${envKey}"${operation === 'set' ? ` = "${envValue}"` : ''}`, 
        `Error: ${error.message}`, 
        'error'
      );
      
    } finally {
      setEnvLoading(false);
    }
  };

  const handleDevChatQuery = async () => {
    if (!devChatQuery.trim()) return;
    
    setDevChatLoading(true);
    setDevChatResult(null);
    
    try {
      const response = await fetch('/api/devchat/query', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ query: devChatQuery }),
      });
      
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }
      
      const data = await response.json();
      setDevChatResult(data);
      
      // Log the test
      addTestLog(
        'DevChat Interpreter', 
        `Query: "${devChatQuery.substring(0, 30)}${devChatQuery.length > 30 ? '...' : ''}"`, 
        `Response received successfully`, 
        'success'
      );
      
    } catch (error) {
      console.error('Error querying DevChat:', error);
      setError('Failed to query DevChat. Please try again.');
      setDevChatResult({ error: error.message });
      
      // Log the test failure
      addTestLog(
        'DevChat Interpreter', 
        `Query: "${devChatQuery.substring(0, 30)}${devChatQuery.length > 30 ? '...' : ''}"`, 
        `Error: ${error.message}`, 
        'error'
      );
      
    } finally {
      setDevChatLoading(false);
    }
  };

  const takeScreenshot = async () => {
    try {
      setLoading(true);
      
      const response = await fetch('/api/tests/manual/screenshot', {
        method: 'POST'
      });
      
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }
      
      const data = await response.json();
      
      if (data.screenshot) {
        setScreenshotData(data.screenshot);
        setOpenScreenshotDialog(true);
        
        // Log the screenshot
        addTestLog(
          'System', 
          'Take screenshot', 
          'Screenshot captured successfully', 
          'success'
        );
      }
    } catch (error) {
      console.error('Error taking screenshot:', error);
      setError('Failed to take screenshot. Please try again.');
      
      // Log the failure
      addTestLog(
        'System', 
        'Take screenshot', 
        `Error: ${error.message}`, 
        'error'
      );
    } finally {
      setLoading(false);
    }
  };

  const clearTestLogs = async () => {
    try {
      await fetch('/api/tests/manual/logs/clear', {
        method: 'POST'
      });
      
      setTestLogs([]);
    } catch (error) {
      console.error('Error clearing test logs:', error);
      setError('Failed to clear test logs. Please try again.');
    }
  };

  const renderChatMessage = (message, index) => {
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
          <Typography variant="body1" sx={{ whiteSpace: 'pre-wrap' }}>
            {message.content}
          </Typography>
        </Paper>
        
        <Typography variant="caption" color="text.secondary" sx={{ mt: 0.5 }}>
          {isUser ? 'You' : 'AI'} • {formattedTime}
        </Typography>
      </Box>
    );
  };

  const getStatusIcon = (status) => {
    switch (status) {
      case 'success':
        return <CheckCircleIcon color="success" />;
      case 'error':
        return <ErrorIcon color="error" />;
      case 'warning':
        return <WarningIcon color="warning" />;
      default:
        return <InfoIcon color="info" />;
    }
  };

  return (
    <Box sx={{ maxWidth: '1200px', mx: 'auto', p: 2 }}>
      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 3 }}>
        <Typography variant="h4" component="h1">
          Manual Testing
        </Typography>
        
        <Box>
          <Button
            variant="outlined"
            color="primary"
            startIcon={<BugReportIcon />}
            onClick={takeScreenshot}
            disabled={loading}
            sx={{ mr: 1 }}
          >
            Take Screenshot
          </Button>
          
          <Button
            variant="contained"
            color="primary"
            startIcon={loading ? <CircularProgress size={24} /> : <RefreshIcon />}
            onClick={clearTestLogs}
            disabled={loading}
          >
            Clear Logs
          </Button>
        </Box>
      </Box>
      
      {error && (
        <Alert severity="error" sx={{ mb: 3 }} onClose={() => setError(null)}>
          {error}
        </Alert>
      )}
      
      <Grid container spacing={3}>
        <Grid item xs={12} md={8}>
          <Paper sx={{ mb: 3 }}>
            <Tabs
              value={activeTab}
              onChange={handleTabChange}
              variant="scrollable"
              scrollButtons="auto"
            >
              <Tab label="Chat Agent" />
              <Tab label="Database Agent" />
              <Tab label="RAG Memory" />
              <Tab label="Custom Tools" />
              <Tab label="Environment Manager" />
              <Tab label="DevChat Interpreter" />
            </Tabs>
            
            <Box sx={{ p: 3 }}>
              {/* Chat Agent Tab */}
              {activeTab === 0 && (
                <Box>
                  <Typography variant="h6" gutterBottom>
                    Chat Agent Testing
                  </Typography>
                  
                  <Paper 
                    elevation={3} 
                    sx={{ 
                      p: 2, 
                      mb: 2, 
                      height: '400px',
                      display: 'flex', 
                      flexDirection: 'column'
                    }}
                  >
                    <Box sx={{ 
                      flexGrow: 1, 
                      overflowY: 'auto', 
                      mb: 2,
                      p: 1
                    }}>
                      {chatMessages.length === 0 ? (
                        <Box sx={{ 
                          height: '100%', 
                          display: 'flex', 
                          flexDirection: 'column', 
                          justifyContent: 'center', 
                          alignItems: 'center',
                          color: 'text.secondary'
                        }}>
                          <Typography variant="body1">
                            No messages yet. Start a conversation to test the Chat Agent.
                          </Typography>
                        </Box>
                      ) : (
                        chatMessages.map(renderChatMessage)
                      )}
                    </Box>
                    
                    <Divider />
                    
                    <Box component="form" onSubmit={handleChatSubmit} sx={{ mt: 2, display: 'flex' }}>
                      <TextField
                        fullWidth
                        placeholder="Type your message..."
                        value={chatInput}
                        onChange={(e) => setChatInput(e.target.value)}
                        variant="outlined"
                        disabled={chatLoading}
                        multiline
                        maxRows={4}
                        sx={{ mr: 1 }}
                      />
                      <Button
                        type="submit"
                        variant="contained"
                        color="primary"
                        disabled={chatLoading || !chatInput.trim()}
                        endIcon={chatLoading ? <CircularProgress size={24} /> : <SendIcon />}
                      >
                        Send
                      </Button>
                    </Box>
                  </Paper>
                  
                  <Typography variant="body2" color="text.secondary">
                    Test the Chat Agent by sending messages and observing responses. Try different types of queries to test various capabilities.
                  </Typography>
                </Box>
              )}
              
              {/* Database Agent Tab */}
              {activeTab === 1 && (
                <Box>
                  <Typography variant="h6" gutterBottom>
                    Database Agent Testing
                  </Typography>
                  
                  <Box sx={{ mb: 3 }}>
                    <TextField
                      fullWidth
                      label="Database Query"
                      placeholder="E.g., 'What do you know about quantum computing?'"
                      value={dbQuery}
                      onChange={(e) => setDbQuery(e.target.value)}
                      variant="outlined"
                      disabled={dbLoading}
                      multiline
                      rows={2}
                      sx={{ mb: 2 }}
                    />
                    
                    <Button
                      variant="contained"
                      color="primary"
                      onClick={handleDbQuery}
                      disabled={dbLoading || !dbQuery.trim()}
                      endIcon={dbLoading ? <CircularProgress size={24} /> : null}
                    >
                      Query Database
                    </Button>
                  </Box>
                  
                  {dbResult && (
                    <Paper sx={{ p: 2, mb: 3, maxHeight: '300px', overflowY: 'auto' }}>
                      <Typography variant="subtitle1" gutterBottom>
                        Query Results:
                      </Typography>
                      
                      {dbResult.error ? (
                        <Alert severity="error">
                          {dbResult.error}
                        </Alert>
                      ) : (
                        <Box>
                          {dbResult.results && dbResult.results.length > 0 ? (
                            <List>
                              {dbResult.results.map((item, index) => (
                                <ListItem key={index} divider={index < dbResult.results.length - 1}>
                                  <ListItemText
                                    primary={item.title || `Result ${index + 1}`}
                                    secondary={item.content || JSON.stringify(item)}
                                  />
                                </ListItem>
                              ))}
                            </List>
                          ) : (
                            <Typography variant="body2" color="text.secondary">
                              No results found for this query.
                            </Typography>
                          )}
                        </Box>
                      )}
                    </Paper>
                  )}
                  
                  <Typography variant="body2" color="text.secondary">
                    Test the Database Agent by querying for information stored in the knowledge base.
                  </Typography>
                </Box>
              )}
              
              {/* RAG Memory Tab */}
              {activeTab === 2 && (
                <Box>
                  <Typography variant="h6" gutterBottom>
                    RAG Memory Testing
                  </Typography>
                  
                  <Box sx={{ mb: 3 }}>
                    <TextField
                      fullWidth
                      label="Memory Query"
                      placeholder="E.g., 'What do you remember about my project?'"
                      value={ragQuery}
                      onChange={(e) => setRagQuery(e.target.value)}
                      variant="outlined"
                      disabled={ragLoading}
                      multiline
                      rows={2}
                      sx={{ mb: 2 }}
                    />
                    
                    <Button
                      variant="contained"
                      color="primary"
                      onClick={handleRagQuery}
                      disabled={ragLoading || !ragQuery.trim()}
                      endIcon={ragLoading ? <CircularProgress size={24} /> : null}
                    >
                      Query Memory
                    </Button>
                  </Box>
                  
                  {ragResult && (
                    <Paper sx={{ p: 2, mb: 3, maxHeight: '300px', overflowY: 'auto' }}>
                      <Typography variant="subtitle1" gutterBottom>
                        Memory Results:
                      </Typography>
                      
                      {ragResult.error ? (
                        <Alert severity="error">
                          {ragResult.error}
                        </Alert>
                      ) : (
                        <Box>
                          {ragResult.memories && ragResult.memories.length > 0 ? (
                            <List>
                              {ragResult.memories.map((memory, index) => (
                                <ListItem key={index} divider={index < ragResult.memories.length - 1}>
                                  <ListItemText
                                    primary={`Memory ${index + 1} (Relevance: ${memory.relevance.toFixed(2)})`}
                                    secondary={
                                      <Box>
                                        <Typography variant="body2" component="span">
                                          {memory.content}
                                        </Typography>
                                        <Typography variant="caption" display="block" color="text.secondary">
                                          {new Date(memory.timestamp).toLocaleString()}
                                        </Typography>
                                      </Box>
                                    }
                                  />
                                </ListItem>
                              ))}
                            </List>
                          ) : (
                            <Typography variant="body2" color="text.secondary">
                              No memories found for this query.
                            </Typography>
                          )}
                          
                          {ragResult.context && (
                            <Box sx={{ mt: 2 }}>
                              <Typography variant="subtitle2" gutterBottom>
                                Generated Context:
                              </Typography>
                              <Paper variant="outlined" sx={{ p: 1 }}>
                                <Typography variant="body2">
                                  {ragResult.context}
                                </Typography>
                              </Paper>
                            </Box>
                          )}
                        </Box>
                      )}
                    </Paper>
                  )}
                  
                  <Typography variant="body2" color="text.secondary">
                    Test the RAG Memory System by querying for memories and observing how they're retrieved and used for context.
                  </Typography>
                </Box>
              )}
              
              {/* Custom Tools Tab */}
              {activeTab === 3 && (
                <Box>
                  <Typography variant="h6" gutterBottom>
                    Custom Tools Testing
                  </Typography>
                  
                  <Box sx={{ mb: 3 }}>
                    <TextField
                      fullWidth
                      label="Tool Name"
                      placeholder="E.g., 'calculator'"
                      value={toolName}
                      onChange={(e) => setToolName(e.target.value)}
                      variant="outlined"
                      disabled={toolLoading}
                      sx={{ mb: 2 }}
                    />
                    
                    <TextField
                      fullWidth
                      label="Tool Parameters (JSON)"
                      placeholder='E.g., {"a": 5, "b": 3, "operation": "add"}'
                      value={toolParams}
                      onChange={(e) => setToolParams(e.target.value)}
                      variant="outlined"
                      disabled={toolLoading}
                      multiline
                      rows={3}
                      sx={{ mb: 2, fontFamily: 'monospace' }}
                    />
                    
                    <Button
                      variant="contained"
                      color="primary"
                      onClick={handleToolExecution}
                      disabled={toolLoading || !toolName.trim()}
                      endIcon={toolLoading ? <CircularProgress size={24} /> : null}
                    >
                      Execute Tool
                    </Button>
                  </Box>
                  
                  {toolResult && (
                    <Paper sx={{ p: 2, mb: 3 }}>
                      <Typography variant="subtitle1" gutterBottom>
                        Tool Execution Result:
                      </Typography>
                      
                      {toolResult.error ? (
                        <Alert severity="error">
                          {toolResult.error}
                        </Alert>
                      ) : (
                        <Box>
                          <SyntaxHighlighter
                            language="javascript"
                            style={vscDarkPlus}
                            customStyle={{ borderRadius: '4px' }}
                          >
                            {JSON.stringify(toolResult.result, null, 2)}
                          </SyntaxHighlighter>
                        </Box>
                      )}
                    </Paper>
                  )}
                  
                  <Typography variant="body2" color="text.secondary">
                    Test Custom Tools by executing them with different parameters and observing the results.
                  </Typography>
                </Box>
              )}
              
              {/* Environment Manager Tab */}
              {activeTab === 4 && (
                <Box>
                  <Typography variant="h6" gutterBottom>
                    Environment Manager Testing
                  </Typography>
                  
                  <Box sx={{ mb: 3 }}>
                    <TextField
                      fullWidth
                      label="Environment Variable Key"
                      placeholder="E.g., 'TEST_API_KEY'"
                      value={envKey}
                      onChange={(e) => setEnvKey(e.target.value)}
                      variant="outlined"
                      disabled={envLoading}
                      sx={{ mb: 2 }}
                    />
                    
                    <TextField
                      fullWidth
                      label="Environment Variable Value"
                      placeholder="E.g., 'test_value_123'"
                      value={envValue}
                      onChange={(e) => setEnvValue(e.target.value)}
                      variant="outlined"
                      disabled={envLoading}
                      sx={{ mb: 2 }}
                    />
                    
                    <Box sx={{ display: 'flex', gap: 1 }}>
                      <Button
                        variant="contained"
                        color="primary"
                        onClick={() => handleEnvOperation('get')}
                        disabled={envLoading || !envKey.trim()}
                      >
                        Get Variable
                      </Button>
                      
                      <Button
                        variant="contained"
                        color="primary"
                        onClick={() => handleEnvOperation('set')}
                        disabled={envLoading || !envKey.trim() || !envValue.trim()}
                      >
                        Set Variable
                      </Button>
                      
                      <Button
                        variant="contained"
                        color="error"
                        onClick={() => handleEnvOperation('delete')}
                        disabled={envLoading || !envKey.trim()}
                      >
                        Delete Variable
                      </Button>
                    </Box>
                  </Box>
                  
                  {envResult && (
                    <Paper sx={{ p: 2, mb: 3 }}>
                      <Typography variant="subtitle1" gutterBottom>
                        Operation Result:
                      </Typography>
                      
                      {envResult.error ? (
                        <Alert severity="error">
                          {envResult.error}
                        </Alert>
                      ) : (
                        <Box>
                          <Alert severity="success" sx={{ mb: 2 }}>
                            {envResult.message || 'Operation completed successfully'}
                          </Alert>
                          
                          {envResult.value !== undefined && (
                            <Typography variant="body1">
                              Value: {envResult.masked ? envResult.value : <code>{envResult.value}</code>}
                            </Typography>
                          )}
                        </Box>
                      )}
                    </Paper>
                  )}
                  
                  <Typography variant="body2" color="text.secondary">
                    Test the Environment Manager by setting, getting, and deleting environment variables.
                  </Typography>
                </Box>
              )}
              
              {/* DevChat Interpreter Tab */}
              {activeTab === 5 && (
                <Box>
                  <Typography variant="h6" gutterBottom>
                    DevChat Interpreter Testing
                  </Typography>
                  
                  <Box sx={{ mb: 3 }}>
                    <TextField
                      fullWidth
                      label="DevChat Query"
                      placeholder="E.g., 'What files are in the project?'"
                      value={devChatQuery}
                      onChange={(e) => setDevChatQuery(e.target.value)}
                      variant="outlined"
                      disabled={devChatLoading}
                      multiline
                      rows={2}
                      sx={{ mb: 2 }}
                    />
                    
                    <Button
                      variant="contained"
                      color="primary"
                      onClick={handleDevChatQuery}
                      disabled={devChatLoading || !devChatQuery.trim()}
                      endIcon={devChatLoading ? <CircularProgress size={24} /> : null}
                    >
                      Query DevChat
                    </Button>
                  </Box>
                  
                  {devChatResult && (
                    <Paper sx={{ p: 2, mb: 3, maxHeight: '300px', overflowY: 'auto' }}>
                      <Typography variant="subtitle1" gutterBottom>
                        DevChat Response:
                      </Typography>
                      
                      {devChatResult.error ? (
                        <Alert severity="error">
                          {devChatResult.error}
                        </Alert>
                      ) : (
                        <Box>
                          <Typography variant="body1" sx={{ whiteSpace: 'pre-wrap' }}>
                            {devChatResult.response}
                          </Typography>
                          
                          {devChatResult.codeMap && (
                            <Box sx={{ mt: 2 }}>
                              <Typography variant="subtitle2" gutterBottom>
                                Code Map:
                              </Typography>
                              <SyntaxHighlighter
                                language="javascript"
                                style={vscDarkPlus}
                                customStyle={{ borderRadius: '4px' }}
                              >
                                {JSON.stringify(devChatResult.codeMap, null, 2)}
                              </SyntaxHighlighter>
                            </Box>
                          )}
                        </Box>
                      )}
                    </Paper>
                  )}
                  
                  <Typography variant="body2" color="text.secondary">
                    Test the DevChat Interpreter by querying about the codebase structure, relationships, and impact analysis.
                  </Typography>
                </Box>
              )}
            </Box>
          </Paper>
        </Grid>
        
        <Grid item xs={12} md={4}>
          <Paper sx={{ p: 3, height: '100%', maxHeight: '700px', display: 'flex', flexDirection: 'column' }}>
            <Typography variant="h6" gutterBottom>
              Test Logs
            </Typography>
            
            <Box sx={{ flexGrow: 1, overflowY: 'auto' }}>
              {testLogs.length === 0 ? (
                <Typography variant="body2" color="text.secondary" align="center" sx={{ mt: 3 }}>
                  No test logs yet. Perform some tests to see logs here.
                </Typography>
              ) : (
                <List>
                  {testLogs.map((log, index) => (
                    <ListItem key={index} divider={index < testLogs.length - 1}>
                      <ListItemIcon>
                        {getStatusIcon(log.status)}
                      </ListItemIcon>
                      <ListItemText
                        primary={
                          <Box sx={{ display: 'flex', alignItems: 'center' }}>
                            <Typography variant="body2" component="span" fontWeight="bold">
                              {log.component}
                            </Typography>
                            <Typography variant="caption" component="span" color="text.secondary" sx={{ ml: 1 }}>
                              {new Date(log.timestamp).toLocaleTimeString()}
                            </Typography>
                          </Box>
                        }
                        secondary={
                          <>
                            <Typography variant="body2" component="span">
                              {log.action}
                            </Typography>
                            <Typography variant="caption" component="div" color={log.status === 'error' ? 'error.main' : 'text.secondary'}>
                              {log.result}
                            </Typography>
                          </>
                        }
                      />
                    </ListItem>
                  ))}
                </List>
              )}
            </Box>
          </Paper>
        </Grid>
      </Grid>
      
      {/* Screenshot Dialog */}
      <Dialog
        open={openScreenshotDialog}
        onClose={() => setOpenScreenshotDialog(false)}
        maxWidth="lg"
        fullWidth
      >
        <DialogTitle>
          Test Screenshot
        </DialogTitle>
        <DialogContent>
          {screenshotData && (
            <Box sx={{ textAlign: 'center' }}>
              <img 
                src={`data:image/png;base64,${screenshotData}`} 
                alt="Test Screenshot" 
                style={{ maxWidth: '100%', maxHeight: '70vh' }}
              />
            </Box>
          )}
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setOpenScreenshotDialog(false)}>
            Close
          </Button>
          {screenshotData && (
            <Button 
              component="a" 
              href={`data:image/png;base64,${screenshotData}`} 
              download="test_screenshot.png"
              color="primary"
            >
              Download
            </Button>
          )}
        </DialogActions>
      </Dialog>
    </Box>
  );
};

export default ManualTesting;
