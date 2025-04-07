import React, { useState, useEffect } from 'react';
import { 
  Box, 
  Typography, 
  Paper, 
  Button, 
  CircularProgress, 
  Alert,
  TextField,
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
import CloudUploadIcon from '@mui/icons-material/CloudUpload';
import CheckCircleIcon from '@mui/icons-material/CheckCircle';
import ErrorIcon from '@mui/icons-material/Error';
import InfoIcon from '@mui/icons-material/Info';
import LinkIcon from '@mui/icons-material/Link';

const DeployWebsite = () => {
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [deploymentStatus, setDeploymentStatus] = useState('idle'); // idle, deploying, success, failed
  const [deploymentLogs, setDeploymentLogs] = useState([]);
  const [deploymentUrl, setDeploymentUrl] = useState('');
  const [deploymentConfig, setDeploymentConfig] = useState({
    apiKey: '',
    siteName: 'ai-agent-system',
    region: 'us-east-1',
    deploymentType: 'static'
  });

  const handleInputChange = (e) => {
    const { name, value } = e.target;
    setDeploymentConfig({
      ...deploymentConfig,
      [name]: value
    });
  };

  const handleDeploy = async () => {
    if (!deploymentConfig.apiKey) {
      setError('API key is required for deployment');
      return;
    }

    setLoading(true);
    setDeploymentStatus('deploying');
    setDeploymentLogs([]);
    setError(null);

    try {
      // Add initial log
      addDeploymentLog('info', 'Starting deployment process...');
      
      // Start deployment
      const response = await fetch('/api/deploy/website', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(deploymentConfig),
      });
      
      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.message || `HTTP error! status: ${response.status}`);
      }
      
      // Set up event source for streaming logs
      const deploymentId = (await response.json()).deploymentId;
      const eventSource = new EventSource(`/api/deploy/logs/${deploymentId}`);
      
      eventSource.onmessage = (event) => {
        const log = JSON.parse(event.data);
        
        if (log.type === 'log') {
          addDeploymentLog(log.level, log.message);
        } else if (log.type === 'status') {
          setDeploymentStatus(log.status);
          
          if (log.status === 'success' && log.url) {
            setDeploymentUrl(log.url);
            addDeploymentLog('success', `Deployment successful! Your website is available at: ${log.url}`);
          } else if (log.status === 'failed') {
            setError(log.message || 'Deployment failed');
            addDeploymentLog('error', `Deployment failed: ${log.message || 'Unknown error'}`);
          }
        }
        
        if (log.type === 'complete' || log.status === 'success' || log.status === 'failed') {
          eventSource.close();
          setLoading(false);
        }
      };
      
      eventSource.onerror = () => {
        eventSource.close();
        setLoading(false);
        setDeploymentStatus('failed');
        setError('Error in deployment stream. Please check logs for details.');
        addDeploymentLog('error', 'Lost connection to deployment service');
      };
      
    } catch (error) {
      console.error('Error deploying website:', error);
      setError(error.message || 'Failed to deploy website');
      setDeploymentStatus('failed');
      addDeploymentLog('error', `Deployment error: ${error.message}`);
      setLoading(false);
    }
  };

  const addDeploymentLog = (level, message) => {
    const log = {
      timestamp: new Date().toISOString(),
      level,
      message
    };
    
    setDeploymentLogs(prev => [...prev, log]);
  };

  const getStatusIcon = (status) => {
    switch (status) {
      case 'success':
        return <CheckCircleIcon color="success" />;
      case 'error':
        return <ErrorIcon color="error" />;
      default:
        return <InfoIcon color="info" />;
    }
  };

  return (
    <Box sx={{ maxWidth: '1200px', mx: 'auto', p: 2 }}>
      <Typography variant="h4" component="h1" gutterBottom>
        Deploy Website
      </Typography>
      
      {error && (
        <Alert severity="error" sx={{ mb: 3 }} onClose={() => setError(null)}>
          {error}
        </Alert>
      )}
      
      <Grid container spacing={3}>
        <Grid item xs={12} md={6}>
          <Paper sx={{ p: 3, mb: 3 }}>
            <Typography variant="h6" gutterBottom>
              Deployment Configuration
            </Typography>
            
            <TextField
              fullWidth
              margin="normal"
              label="API Key"
              name="apiKey"
              type="password"
              value={deploymentConfig.apiKey}
              onChange={handleInputChange}
              required
              disabled={loading}
            />
            
            <TextField
              fullWidth
              margin="normal"
              label="Site Name"
              name="siteName"
              value={deploymentConfig.siteName}
              onChange={handleInputChange}
              required
              disabled={loading}
              helperText="This will be part of your website URL"
            />
            
            <TextField
              fullWidth
              margin="normal"
              label="Region"
              name="region"
              value={deploymentConfig.region}
              onChange={handleInputChange}
              disabled={loading}
              helperText="Server region for your deployment"
            />
            
            <Box sx={{ mt: 3 }}>
              <Button
                variant="contained"
                color="primary"
                startIcon={loading ? <CircularProgress size={24} /> : <CloudUploadIcon />}
                onClick={handleDeploy}
                disabled={loading || !deploymentConfig.apiKey}
                fullWidth
              >
                {loading ? 'Deploying...' : 'Deploy Website'}
              </Button>
            </Box>
          </Paper>
          
          {deploymentStatus === 'success' && deploymentUrl && (
            <Card sx={{ mb: 3 }}>
              <CardContent>
                <Typography variant="h6" color="success.main" gutterBottom>
                  <CheckCircleIcon sx={{ mr: 1, verticalAlign: 'middle' }} />
                  Deployment Successful!
                </Typography>
                
                <Typography variant="body1" paragraph>
                  Your website has been successfully deployed and is now available at:
                </Typography>
                
                <Box sx={{ 
                  p: 2, 
                  bgcolor: 'background.paper', 
                  borderRadius: 1, 
                  border: 1, 
                  borderColor: 'divider',
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'space-between'
                }}>
                  <Typography variant="body1" component="div" sx={{ fontWeight: 'bold' }}>
                    <LinkIcon sx={{ mr: 1, verticalAlign: 'middle' }} />
                    {deploymentUrl}
                  </Typography>
                  
                  <Button 
                    variant="outlined" 
                    size="small"
                    onClick={() => window.open(deploymentUrl, '_blank')}
                  >
                    Visit
                  </Button>
                </Box>
              </CardContent>
              <CardActions>
                <Button 
                  size="small" 
                  onClick={() => navigator.clipboard.writeText(deploymentUrl)}
                >
                  Copy URL
                </Button>
              </CardActions>
            </Card>
          )}
        </Grid>
        
        <Grid item xs={12} md={6}>
          <Paper sx={{ p: 3, height: '100%', maxHeight: '600px', display: 'flex', flexDirection: 'column' }}>
            <Typography variant="h6" gutterBottom>
              Deployment Logs
            </Typography>
            
            <Box sx={{ flexGrow: 1, overflowY: 'auto' }}>
              {deploymentLogs.length === 0 ? (
                <Typography variant="body2" color="text.secondary" align="center" sx={{ mt: 3 }}>
                  No deployment logs yet. Start the deployment to see logs here.
                </Typography>
              ) : (
                <List>
                  {deploymentLogs.map((log, index) => (
                    <ListItem key={index} divider={index < deploymentLogs.length - 1}>
                      <ListItemIcon>
                        {getStatusIcon(log.level)}
                      </ListItemIcon>
                      <ListItemText
                        primary={
                          <Box sx={{ display: 'flex', alignItems: 'center' }}>
                            <Typography variant="body2" component="span">
                              {log.message}
                            </Typography>
                          </Box>
                        }
                        secondary={
                          <Typography variant="caption" component="span" color="text.secondary">
                            {new Date(log.timestamp).toLocaleTimeString()}
                          </Typography>
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
    </Box>
  );
};

export default DeployWebsite;
