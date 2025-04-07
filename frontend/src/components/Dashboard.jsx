import React from 'react';
import { Box, Typography, Paper, Grid, Card, CardContent, CardHeader, Divider, Button, CircularProgress } from '@mui/material';
import DashboardIcon from '@mui/icons-material/Dashboard';
import ChatIcon from '@mui/icons-material/Chat';
import BuildIcon from '@mui/icons-material/Build';
import TaskIcon from '@mui/icons-material/Task';
import CodeIcon from '@mui/icons-material/Code';
import MemoryIcon from '@mui/icons-material/Memory';
import StorageIcon from '@mui/icons-material/Storage';

const Dashboard = () => {
  const [systemStatus, setSystemStatus] = React.useState({
    loading: true,
    status: 'unknown',
    components: {},
    stats: {}
  });

  React.useEffect(() => {
    fetchSystemStatus();
    // Set up polling for system status every 30 seconds
    const interval = setInterval(fetchSystemStatus, 30000);
    return () => clearInterval(interval);
  }, []);

  const fetchSystemStatus = async () => {
    try {
      setSystemStatus(prev => ({ ...prev, loading: true }));
      const response = await fetch('/api/system/status');
      if (!response.ok) {
        throw new Error(`Error: ${response.statusText}`);
      }
      
      const data = await response.json();
      setSystemStatus({
        loading: false,
        status: data.status,
        components: data.components || {},
        stats: data.stats || {}
      });
    } catch (error) {
      console.error('Error fetching system status:', error);
      setSystemStatus(prev => ({ 
        ...prev, 
        loading: false,
        status: 'error'
      }));
    }
  };

  // Mock data for demonstration
  const mockStats = {
    conversations: 128,
    tools: 15,
    tasks: 42,
    knowledge_entries: 256,
    memory_size: '1.2 GB',
    uptime: '3 days, 7 hours',
    recent_activity: [
      { type: 'conversation', timestamp: '2025-04-07T12:45:23Z', description: 'Chat about system architecture' },
      { type: 'task', timestamp: '2025-04-07T11:30:15Z', description: 'Optimize database queries' },
      { type: 'tool', timestamp: '2025-04-07T10:15:42Z', description: 'Added new data visualization tool' },
    ]
  };

  const mockComponents = {
    interpreter: 'active',
    rag: 'active',
    database: 'active',
    tools: 'active',
    tasks: 'active',
    development_agent: 'active'
  };

  // Use mock data if real data is not available
  const stats = systemStatus.stats.conversations ? systemStatus.stats : mockStats;
  const components = Object.keys(systemStatus.components).length > 0 ? systemStatus.components : mockComponents;

  const getStatusColor = (status) => {
    switch (status) {
      case 'active':
        return 'success.main';
      case 'warning':
        return 'warning.main';
      case 'error':
        return 'error.main';
      case 'inactive':
        return 'text.disabled';
      default:
        return 'info.main';
    }
  };

  return (
    <Box sx={{ maxWidth: '1200px', mx: 'auto', p: 2 }}>
      <Typography variant="h4" component="h1" gutterBottom>
        System Dashboard
      </Typography>
      
      {/* System Status */}
      <Paper sx={{ p: 2, mb: 3 }}>
        <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
          <Typography variant="h6">
            System Status: {' '}
            <span style={{ 
              color: systemStatus.status === 'online' ? 'green' : 
                     systemStatus.status === 'error' ? 'red' : 'orange'
            }}>
              {systemStatus.status === 'online' ? 'Online' : 
               systemStatus.status === 'error' ? 'Error' : 'Unknown'}
            </span>
          </Typography>
          <Button 
            variant="outlined" 
            onClick={fetchSystemStatus}
            startIcon={systemStatus.loading ? <CircularProgress size={16} /> : null}
            disabled={systemStatus.loading}
          >
            Refresh
          </Button>
        </Box>
        
        <Typography variant="body2" color="text.secondary">
          Uptime: {stats.uptime}
        </Typography>
      </Paper>
      
      {/* Component Status Cards */}
      <Typography variant="h6" gutterBottom>
        Component Status
      </Typography>
      
      <Grid container spacing={2} sx={{ mb: 3 }}>
        <Grid item xs={12} sm={6} md={4}>
          <Card>
            <CardHeader 
              avatar={<ChatIcon />}
              title="Interpreter"
              subheader={
                <Typography 
                  variant="body2" 
                  sx={{ color: getStatusColor(components.interpreter) }}
                >
                  {components.interpreter}
                </Typography>
              }
            />
          </Card>
        </Grid>
        
        <Grid item xs={12} sm={6} md={4}>
          <Card>
            <CardHeader 
              avatar={<MemoryIcon />}
              title="RAG Memory System"
              subheader={
                <Typography 
                  variant="body2" 
                  sx={{ color: getStatusColor(components.rag) }}
                >
                  {components.rag}
                </Typography>
              }
            />
          </Card>
        </Grid>
        
        <Grid item xs={12} sm={6} md={4}>
          <Card>
            <CardHeader 
              avatar={<StorageIcon />}
              title="Database"
              subheader={
                <Typography 
                  variant="body2" 
                  sx={{ color: getStatusColor(components.database) }}
                >
                  {components.database}
                </Typography>
              }
            />
          </Card>
        </Grid>
        
        <Grid item xs={12} sm={6} md={4}>
          <Card>
            <CardHeader 
              avatar={<BuildIcon />}
              title="Tools System"
              subheader={
                <Typography 
                  variant="body2" 
                  sx={{ color: getStatusColor(components.tools) }}
                >
                  {components.tools}
                </Typography>
              }
            />
          </Card>
        </Grid>
        
        <Grid item xs={12} sm={6} md={4}>
          <Card>
            <CardHeader 
              avatar={<TaskIcon />}
              title="Task Manager"
              subheader={
                <Typography 
                  variant="body2" 
                  sx={{ color: getStatusColor(components.tasks) }}
                >
                  {components.tasks}
                </Typography>
              }
            />
          </Card>
        </Grid>
        
        <Grid item xs={12} sm={6} md={4}>
          <Card>
            <CardHeader 
              avatar={<CodeIcon />}
              title="Development Agent"
              subheader={
                <Typography 
                  variant="body2" 
                  sx={{ color: getStatusColor(components.development_agent) }}
                >
                  {components.development_agent}
                </Typography>
              }
            />
          </Card>
        </Grid>
      </Grid>
      
      {/* System Statistics */}
      <Typography variant="h6" gutterBottom>
        System Statistics
      </Typography>
      
      <Grid container spacing={2} sx={{ mb: 3 }}>
        <Grid item xs={6} sm={3}>
          <Card>
            <CardContent>
              <Typography variant="h4" align="center">
                {stats.conversations}
              </Typography>
              <Typography variant="body2" color="text.secondary" align="center">
                Conversations
              </Typography>
            </CardContent>
          </Card>
        </Grid>
        
        <Grid item xs={6} sm={3}>
          <Card>
            <CardContent>
              <Typography variant="h4" align="center">
                {stats.tools}
              </Typography>
              <Typography variant="body2" color="text.secondary" align="center">
                Tools
              </Typography>
            </CardContent>
          </Card>
        </Grid>
        
        <Grid item xs={6} sm={3}>
          <Card>
            <CardContent>
              <Typography variant="h4" align="center">
                {stats.tasks}
              </Typography>
              <Typography variant="body2" color="text.secondary" align="center">
                Tasks
              </Typography>
            </CardContent>
          </Card>
        </Grid>
        
        <Grid item xs={6} sm={3}>
          <Card>
            <CardContent>
              <Typography variant="h4" align="center">
                {stats.knowledge_entries}
              </Typography>
              <Typography variant="body2" color="text.secondary" align="center">
                Knowledge Entries
              </Typography>
            </CardContent>
          </Card>
        </Grid>
      </Grid>
      
      {/* Recent Activity */}
      <Typography variant="h6" gutterBottom>
        Recent Activity
      </Typography>
      
      <Paper sx={{ p: 2 }}>
        {stats.recent_activity && stats.recent_activity.length > 0 ? (
          <Box>
            {stats.recent_activity.map((activity, index) => (
              <Box key={index}>
                <Box sx={{ display: 'flex', justifyContent: 'space-between', py: 1 }}>
                  <Box>
                    <Typography variant="body2">
                      {activity.description}
                    </Typography>
                    <Typography variant="caption" color="text.secondary">
                      {activity.type}
                    </Typography>
                  </Box>
                  <Typography variant="caption" color="text.secondary">
                    {new Date(activity.timestamp).toLocaleString()}
                  </Typography>
                </Box>
                {index < stats.recent_activity.length - 1 && <Divider />}
              </Box>
            ))}
          </Box>
        ) : (
          <Typography variant="body2" color="text.secondary">
            No recent activity.
          </Typography>
        )}
      </Paper>
    </Box>
  );
};

export default Dashboard;
