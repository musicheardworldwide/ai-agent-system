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
  ListItemIcon
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

const TestRunner = () => {
  const [activeTab, setActiveTab] = useState(0);
  const [loading, setLoading] = useState(false);
  const [testResults, setTestResults] = useState({});
  const [error, setError] = useState(null);
  const [testStatus, setTestStatus] = useState({
    chat: 'pending',
    database: 'pending',
    rag: 'pending',
    tools: 'pending',
    env: 'pending',
    devchat: 'pending'
  });
  const [testLogs, setTestLogs] = useState({});

  useEffect(() => {
    // Load any saved test results
    const loadTestResults = async () => {
      try {
        const response = await fetch('/api/tests/results');
        if (response.ok) {
          const data = await response.json();
          if (data.results) {
            setTestResults(data.results);
            
            // Update status based on results
            const newStatus = { ...testStatus };
            Object.keys(data.results).forEach(component => {
              if (data.results[component]) {
                newStatus[component] = data.results[component].success ? 'success' : 'failed';
              }
            });
            setTestStatus(newStatus);
          }
        }
      } catch (error) {
        console.error('Error loading test results:', error);
      }
    };
    
    loadTestResults();
  }, []);

  const handleTabChange = (event, newValue) => {
    setActiveTab(newValue);
  };

  const runTest = async (component) => {
    try {
      setLoading(true);
      setError(null);
      
      // Update status to running
      setTestStatus(prev => ({
        ...prev,
        [component]: 'running'
      }));
      
      // Clear previous logs
      setTestLogs(prev => ({
        ...prev,
        [component]: []
      }));
      
      // Start test
      const response = await fetch(`/api/tests/run/${component}`, {
        method: 'POST'
      });
      
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }
      
      // Set up event source for streaming logs
      const eventSource = new EventSource(`/api/tests/logs/${component}`);
      
      eventSource.onmessage = (event) => {
        const log = JSON.parse(event.data);
        setTestLogs(prev => ({
          ...prev,
          [component]: [...(prev[component] || []), log]
        }));
      };
      
      eventSource.onerror = () => {
        eventSource.close();
      };
      
      // Poll for test completion
      const checkStatus = async () => {
        const statusResponse = await fetch(`/api/tests/status/${component}`);
        if (statusResponse.ok) {
          const statusData = await statusResponse.json();
          
          if (statusData.status === 'completed' || statusData.status === 'failed') {
            eventSource.close();
            
            // Get final results
            const resultsResponse = await fetch(`/api/tests/results/${component}`);
            if (resultsResponse.ok) {
              const resultsData = await resultsResponse.json();
              
              setTestResults(prev => ({
                ...prev,
                [component]: resultsData
              }));
              
              setTestStatus(prev => ({
                ...prev,
                [component]: statusData.status === 'completed' ? 'success' : 'failed'
              }));
              
              setLoading(false);
            }
          } else {
            // Continue polling
            setTimeout(checkStatus, 1000);
          }
        }
      };
      
      checkStatus();
      
    } catch (error) {
      console.error(`Error running ${component} test:`, error);
      setError(`Failed to run ${component} test: ${error.message}`);
      setTestStatus(prev => ({
        ...prev,
        [component]: 'failed'
      }));
      setLoading(false);
    }
  };

  const runAllTests = async () => {
    try {
      setLoading(true);
      setError(null);
      
      // Update all statuses to running
      const components = ['chat', 'database', 'rag', 'tools', 'env', 'devchat'];
      const newStatus = {};
      components.forEach(component => {
        newStatus[component] = 'running';
      });
      setTestStatus(newStatus);
      
      // Clear all logs
      setTestLogs({});
      
      // Start all tests
      const response = await fetch('/api/tests/run/all', {
        method: 'POST'
      });
      
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }
      
      // Poll for all tests completion
      const checkAllStatus = async () => {
        const statusResponse = await fetch('/api/tests/status/all');
        if (statusResponse.ok) {
          const statusData = await statusResponse.json();
          
          // Update individual test statuses
          setTestStatus(statusData.statuses);
          
          if (statusData.allCompleted) {
            // Get final results
            const resultsResponse = await fetch('/api/tests/results');
            if (resultsResponse.ok) {
              const resultsData = await resultsResponse.json();
              setTestResults(resultsData.results);
            }
            
            setLoading(false);
          } else {
            // Continue polling
            setTimeout(checkAllStatus, 1000);
          }
        }
      };
      
      checkAllStatus();
      
    } catch (error) {
      console.error('Error running all tests:', error);
      setError(`Failed to run all tests: ${error.message}`);
      setLoading(false);
    }
  };

  const getStatusIcon = (status) => {
    switch (status) {
      case 'success':
        return <CheckCircleIcon color="success" />;
      case 'failed':
        return <ErrorIcon color="error" />;
      case 'running':
        return <CircularProgress size={24} />;
      case 'warning':
        return <WarningIcon color="warning" />;
      default:
        return <InfoIcon color="disabled" />;
    }
  };

  const getComponentIcon = (component) => {
    switch (component) {
      case 'chat':
        return <TerminalIcon />;
      case 'database':
        return <StorageIcon />;
      case 'rag':
        return <MemoryIcon />;
      case 'tools':
        return <BuildIcon />;
      case 'env':
        return <VpnKeyIcon />;
      case 'devchat':
        return <CodeIcon />;
      default:
        return <InfoIcon />;
    }
  };

  const renderTestCard = (component, title) => {
    const result = testResults[component];
    const status = testStatus[component];
    
    return (
      <Grid item xs={12} md={6} lg={4}>
        <Card variant="outlined">
          <CardContent>
            <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 2 }}>
              <Box sx={{ display: 'flex', alignItems: 'center' }}>
                {getComponentIcon(component)}
                <Typography variant="h6" sx={{ ml: 1 }}>
                  {title}
                </Typography>
              </Box>
              {getStatusIcon(status)}
            </Box>
            
            {result && (
              <>
                <Typography variant="body2" color="text.secondary" gutterBottom>
                  {result.testsRun} tests run, {result.testsPassed} passed, {result.testsFailed} failed
                </Typography>
                
                {result.success ? (
                  <Alert severity="success" sx={{ mt: 1 }}>
                    All tests passed successfully
                  </Alert>
                ) : (
                  <Alert severity="error" sx={{ mt: 1 }}>
                    Some tests failed
                  </Alert>
                )}
              </>
            )}
            
            {!result && status === 'pending' && (
              <Typography variant="body2" color="text.secondary">
                Test not run yet
              </Typography>
            )}
          </CardContent>
          <CardActions>
            <Button 
              size="small" 
              startIcon={status === 'running' ? <CircularProgress size={16} /> : <PlayArrowIcon />}
              onClick={() => runTest(component)}
              disabled={status === 'running' || loading}
            >
              Run Test
            </Button>
            <Button 
              size="small"
              onClick={() => setActiveTab(component === 'chat' ? 0 : 
                                         component === 'database' ? 1 : 
                                         component === 'rag' ? 2 : 
                                         component === 'tools' ? 3 : 
                                         component === 'env' ? 4 : 5)}
            >
              View Details
            </Button>
          </CardActions>
        </Card>
      </Grid>
    );
  };

  const renderTestDetails = (component) => {
    const result = testResults[component];
    const logs = testLogs[component] || [];
    
    if (!result && logs.length === 0) {
      return (
        <Paper sx={{ p: 3, mt: 3 }}>
          <Typography variant="body1" color="text.secondary" align="center">
            No test results available. Run the test to see details.
          </Typography>
        </Paper>
      );
    }
    
    return (
      <Paper sx={{ p: 3, mt: 3 }}>
        {result && (
          <>
            <Typography variant="h6" gutterBottom>
              Test Results
            </Typography>
            
            <Box sx={{ mb: 3 }}>
              <Typography variant="body2" gutterBottom>
                <strong>Status:</strong> {result.success ? 'Success' : 'Failed'}
              </Typography>
              <Typography variant="body2" gutterBottom>
                <strong>Tests Run:</strong> {result.testsRun}
              </Typography>
              <Typography variant="body2" gutterBottom>
                <strong>Tests Passed:</strong> {result.testsPassed}
              </Typography>
              <Typography variant="body2" gutterBottom>
                <strong>Tests Failed:</strong> {result.testsFailed}
              </Typography>
              <Typography variant="body2" gutterBottom>
                <strong>Duration:</strong> {result.duration}ms
              </Typography>
            </Box>
            
            <Divider sx={{ mb: 3 }} />
          </>
        )}
        
        <Typography variant="h6" gutterBottom>
          Test Logs
        </Typography>
        
        {logs.length > 0 ? (
          <List sx={{ bgcolor: 'background.paper', border: 1, borderColor: 'divider', borderRadius: 1 }}>
            {logs.map((log, index) => (
              <ListItem key={index} divider={index < logs.length - 1}>
                <ListItemIcon>
                  {log.level === 'error' ? <ErrorIcon color="error" /> :
                   log.level === 'warning' ? <WarningIcon color="warning" /> :
                   log.level === 'success' ? <CheckCircleIcon color="success" /> :
                   <InfoIcon color="info" />}
                </ListItemIcon>
                <ListItemText
                  primary={log.message}
                  secondary={log.timestamp}
                />
              </ListItem>
            ))}
          </List>
        ) : (
          <Typography variant="body2" color="text.secondary">
            No logs available
          </Typography>
        )}
      </Paper>
    );
  };

  return (
    <Box sx={{ maxWidth: '1200px', mx: 'auto', p: 2 }}>
      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 3 }}>
        <Typography variant="h4" component="h1">
          System Testing
        </Typography>
        
        <Button
          variant="contained"
          color="primary"
          startIcon={loading ? <CircularProgress size={24} /> : <RefreshIcon />}
          onClick={runAllTests}
          disabled={loading}
        >
          Run All Tests
        </Button>
      </Box>
      
      {error && (
        <Alert severity="error" sx={{ mb: 3 }} onClose={() => setError(null)}>
          {error}
        </Alert>
      )}
      
      <Paper sx={{ p: 3, mb: 3 }}>
        <Typography variant="h6" gutterBottom>
          Test Overview
        </Typography>
        
        <Grid container spacing={3}>
          {renderTestCard('chat', 'Chat Agent')}
          {renderTestCard('database', 'Database Agent')}
          {renderTestCard('rag', 'RAG Memory')}
          {renderTestCard('tools', 'Custom Tools')}
          {renderTestCard('env', 'Environment Manager')}
          {renderTestCard('devchat', 'DevChat Interpreter')}
        </Grid>
      </Paper>
      
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
      </Paper>
      
      {activeTab === 0 && renderTestDetails('chat')}
      {activeTab === 1 && renderTestDetails('database')}
      {activeTab === 2 && renderTestDetails('rag')}
      {activeTab === 3 && renderTestDetails('tools')}
      {activeTab === 4 && renderTestDetails('env')}
      {activeTab === 5 && renderTestDetails('devchat')}
    </Box>
  );
};

export default TestRunner;
