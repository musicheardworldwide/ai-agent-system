import React from 'react';
import { Box, Typography, Paper, Grid, Card, CardContent, CardActions, Button, Divider } from '@mui/material';
import CodeEditor from './CodeEditor';

const CodeDevelopmentAgent = () => {
  const [agentStatus, setAgentStatus] = React.useState('idle');
  const [currentTask, setCurrentTask] = React.useState(null);
  const [proposedChanges, setProposedChanges] = React.useState(null);
  const [logs, setLogs] = React.useState([]);

  // Mock function to start the agent
  const startAgent = () => {
    setAgentStatus('analyzing');
    setLogs(prev => [...prev, {
      timestamp: new Date().toISOString(),
      level: 'info',
      message: 'Development agent started analyzing codebase'
    }]);
    
    // Simulate agent finding an improvement after 3 seconds
    setTimeout(() => {
      setAgentStatus('proposing');
      setCurrentTask({
        id: 'task-1',
        description: 'Optimize database query in RAG memory system',
        file: '/app/rag.py',
        lineStart: 120,
        lineEnd: 135
      });
      setProposedChanges({
        original: `    def retrieve_context(self, query, n_results=5, include_metadata=True):
        """Retrieve relevant context based on query"""
        # Generate embedding for the query
        query_embedding = self.generate_embedding(query)
        
        # Search in conversations
        conv_results = self.conversations_collection.query(
            query_embeddings=[query_embedding],
            n_results=n_results
        )`,
        proposed: `    def retrieve_context(self, query, n_results=5, include_metadata=True, filter_criteria=None):
        """Retrieve relevant context based on query with optional filtering"""
        # Generate embedding for the query
        query_embedding = self.generate_embedding(query)
        
        # Prepare filter if provided
        where_filter = filter_criteria if filter_criteria else None
        
        # Search in conversations with optimized parameters
        conv_results = self.conversations_collection.query(
            query_embeddings=[query_embedding],
            n_results=n_results,
            where=where_filter,
            include=['documents', 'metadatas', 'distances']
        )`
      });
      setLogs(prev => [...prev, {
        timestamp: new Date().toISOString(),
        level: 'info',
        message: 'Development agent found potential optimization in RAG memory system'
      }]);
    }, 3000);
  };

  // Mock function to accept changes
  const acceptChanges = () => {
    setAgentStatus('implementing');
    setLogs(prev => [...prev, {
      timestamp: new Date().toISOString(),
      level: 'info',
      message: 'Implementing approved changes to RAG memory system'
    }]);
    
    // Simulate implementation
    setTimeout(() => {
      setAgentStatus('testing');
      setLogs(prev => [...prev, {
        timestamp: new Date().toISOString(),
        level: 'info',
        message: 'Testing implemented changes'
      }]);
      
      // Simulate successful test
      setTimeout(() => {
        setAgentStatus('completed');
        setLogs(prev => [...prev, {
          timestamp: new Date().toISOString(),
          level: 'success',
          message: 'Changes successfully implemented and tested. Performance improved by 15%.'
        }]);
        
        // Reset after some time
        setTimeout(() => {
          setAgentStatus('idle');
          setCurrentTask(null);
          setProposedChanges(null);
        }, 5000);
      }, 2000);
    }, 2000);
  };

  // Mock function to reject changes
  const rejectChanges = () => {
    setAgentStatus('idle');
    setLogs(prev => [...prev, {
      timestamp: new Date().toISOString(),
      level: 'info',
      message: 'Changes rejected by user'
    }]);
    setCurrentTask(null);
    setProposedChanges(null);
  };

  return (
    <Box sx={{ maxWidth: '1000px', mx: 'auto', p: 2 }}>
      <Typography variant="h4" component="h1" gutterBottom>
        Self-Improving Code Development Agent
      </Typography>
      
      <Paper sx={{ p: 2, mb: 3 }}>
        <Typography variant="h6" gutterBottom>
          Status: <span style={{ 
            color: agentStatus === 'idle' ? 'gray' : 
                   agentStatus === 'analyzing' ? 'blue' :
                   agentStatus === 'proposing' ? 'orange' :
                   agentStatus === 'implementing' ? 'purple' :
                   agentStatus === 'testing' ? 'teal' :
                   agentStatus === 'completed' ? 'green' : 'black'
          }}>
            {agentStatus.charAt(0).toUpperCase() + agentStatus.slice(1)}
          </span>
        </Typography>
        
        <Typography variant="body1" paragraph>
          This agent continuously monitors the system's codebase, identifies potential improvements, 
          and proposes changes. You can review, accept, or reject these proposals.
        </Typography>
        
        {agentStatus === 'idle' && (
          <Button 
            variant="contained" 
            color="primary" 
            onClick={startAgent}
          >
            Start Development Agent
          </Button>
        )}
      </Paper>
      
      {currentTask && proposedChanges && (
        <Paper sx={{ p: 2, mb: 3 }}>
          <Typography variant="h6" gutterBottom>
            Proposed Improvement
          </Typography>
          
          <Typography variant="subtitle1">
            {currentTask.description}
          </Typography>
          
          <Typography variant="body2" color="text.secondary" gutterBottom>
            File: {currentTask.file} (Lines {currentTask.lineStart}-{currentTask.lineEnd})
          </Typography>
          
          <Grid container spacing={2} sx={{ mt: 2 }}>
            <Grid item xs={12} md={6}>
              <Typography variant="subtitle2" gutterBottom>
                Original Code:
              </Typography>
              <Box sx={{ border: 1, borderColor: 'grey.300', borderRadius: 1 }}>
                <CodeEditor
                  value={proposedChanges.original}
                  language="python"
                  height="200px"
                  readOnly={true}
                />
              </Box>
            </Grid>
            <Grid item xs={12} md={6}>
              <Typography variant="subtitle2" gutterBottom>
                Proposed Code:
              </Typography>
              <Box sx={{ border: 1, borderColor: 'grey.300', borderRadius: 1 }}>
                <CodeEditor
                  value={proposedChanges.proposed}
                  language="python"
                  height="200px"
                  readOnly={true}
                />
              </Box>
            </Grid>
          </Grid>
          
          {agentStatus === 'proposing' && (
            <Box sx={{ mt: 2, display: 'flex', justifyContent: 'flex-end' }}>
              <Button 
                variant="outlined" 
                color="error" 
                onClick={rejectChanges}
                sx={{ mr: 1 }}
              >
                Reject
              </Button>
              <Button 
                variant="contained" 
                color="success" 
                onClick={acceptChanges}
              >
                Accept Changes
              </Button>
            </Box>
          )}
        </Paper>
      )}
      
      <Paper sx={{ p: 2 }}>
        <Typography variant="h6" gutterBottom>
          Development Agent Logs
        </Typography>
        
        <Box sx={{ maxHeight: '300px', overflowY: 'auto' }}>
          {logs.length === 0 ? (
            <Typography variant="body2" color="text.secondary">
              No activity logs yet.
            </Typography>
          ) : (
            logs.map((log, index) => (
              <Box key={index} sx={{ mb: 1 }}>
                <Typography variant="caption" color="text.secondary">
                  {new Date(log.timestamp).toLocaleString()}
                </Typography>
                <Typography 
                  variant="body2" 
                  sx={{ 
                    color: log.level === 'error' ? 'error.main' : 
                           log.level === 'warning' ? 'warning.main' :
                           log.level === 'success' ? 'success.main' : 'inherit'
                  }}
                >
                  {log.message}
                </Typography>
                {index < logs.length - 1 && <Divider sx={{ my: 1 }} />}
              </Box>
            ))
          )}
        </Box>
      </Paper>
    </Box>
  );
};

export default CodeDevelopmentAgent;
