import React, { useState, useEffect } from 'react';
import { 
  Box, 
  Typography, 
  Paper, 
  List, 
  ListItem, 
  ListItemText, 
  ListItemIcon,
  Button,
  TextField,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  IconButton,
  Chip,
  Divider,
  CircularProgress,
  Alert,
  Tooltip,
  Grid,
  Card,
  CardContent,
  CardActions
} from '@mui/material';
import AddIcon from '@mui/icons-material/Add';
import EditIcon from '@mui/icons-material/Edit';
import DeleteIcon from '@mui/icons-material/Delete';
import PlayArrowIcon from '@mui/icons-material/PlayArrow';
import BuildIcon from '@mui/icons-material/Build';
import { Prism as SyntaxHighlighter } from 'react-syntax-highlighter';
import { vscDarkPlus } from 'react-syntax-highlighter/dist/esm/styles/prism';

const Tools = () => {
  const [tools, setTools] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [openDialog, setOpenDialog] = useState(false);
  const [editingTool, setEditingTool] = useState(null);
  const [formData, setFormData] = useState({
    name: '',
    description: '',
    code: '',
    parameters: '',
    examples: ''
  });
  const [testResult, setTestResult] = useState(null);
  const [testLoading, setTestLoading] = useState(false);

  useEffect(() => {
    fetchTools();
  }, []);

  const fetchTools = async () => {
    try {
      setLoading(true);
      const response = await fetch('/api/tools');
      
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }
      
      const data = await response.json();
      setTools(data.tools || []);
    } catch (error) {
      console.error('Error fetching tools:', error);
      setError('Failed to load tools. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  const handleOpenDialog = (tool = null) => {
    if (tool) {
      // Editing existing tool
      setEditingTool(tool);
      setFormData({
        name: tool.name,
        description: tool.description,
        code: tool.code,
        parameters: JSON.stringify(tool.parameters || {}, null, 2),
        examples: JSON.stringify(tool.examples || [], null, 2)
      });
    } else {
      // Creating new tool
      setEditingTool(null);
      setFormData({
        name: '',
        description: '',
        code: 'def tool_function(parameter1, parameter2):\n    """\n    Tool description\n    \n    Args:\n        parameter1: Description of parameter1\n        parameter2: Description of parameter2\n        \n    Returns:\n        Result description\n    """\n    # Your code here\n    result = parameter1 + parameter2\n    return result',
        parameters: JSON.stringify({
          "parameter1": {
            "type": "string",
            "description": "Description of parameter1"
          },
          "parameter2": {
            "type": "number",
            "description": "Description of parameter2"
          }
        }, null, 2),
        examples: JSON.stringify([
          {
            "parameter1": "example",
            "parameter2": 42,
            "result": "example42"
          }
        ], null, 2)
      });
    }
    
    setOpenDialog(true);
  };

  const handleCloseDialog = () => {
    setOpenDialog(false);
    setTestResult(null);
  };

  const handleInputChange = (e) => {
    const { name, value } = e.target;
    setFormData({
      ...formData,
      [name]: value
    });
  };

  const validateForm = () => {
    // Check required fields
    if (!formData.name || !formData.description || !formData.code) {
      setError('Name, description, and code are required');
      return false;
    }
    
    // Validate JSON fields
    try {
      if (formData.parameters) {
        JSON.parse(formData.parameters);
      }
      if (formData.examples) {
        JSON.parse(formData.examples);
      }
    } catch (e) {
      setError('Invalid JSON in parameters or examples');
      return false;
    }
    
    return true;
  };

  const handleSubmit = async () => {
    if (!validateForm()) return;
    
    try {
      setLoading(true);
      setError(null);
      
      const toolData = {
        name: formData.name,
        description: formData.description,
        code: formData.code,
        parameters: formData.parameters ? JSON.parse(formData.parameters) : {},
        examples: formData.examples ? JSON.parse(formData.examples) : []
      };
      
      const url = editingTool 
        ? `/api/tools/${editingTool.id}` 
        : '/api/tools';
      
      const method = editingTool ? 'PUT' : 'POST';
      
      const response = await fetch(url, {
        method,
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(toolData),
      });
      
      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.message || `HTTP error! status: ${response.status}`);
      }
      
      // Refresh tools list
      await fetchTools();
      
      // Close dialog
      handleCloseDialog();
    } catch (error) {
      console.error('Error saving tool:', error);
      setError(error.message || 'Failed to save tool. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  const handleDeleteTool = async (toolId) => {
    if (!window.confirm('Are you sure you want to delete this tool?')) {
      return;
    }
    
    try {
      setLoading(true);
      
      const response = await fetch(`/api/tools/${toolId}`, {
        method: 'DELETE',
      });
      
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }
      
      // Refresh tools list
      await fetchTools();
    } catch (error) {
      console.error('Error deleting tool:', error);
      setError('Failed to delete tool. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  const handleTestTool = async () => {
    if (!validateForm()) return;
    
    try {
      setTestLoading(true);
      setTestResult(null);
      setError(null);
      
      const testData = {
        code: formData.code,
        parameters: formData.parameters ? JSON.parse(formData.parameters) : {},
        examples: formData.examples ? JSON.parse(formData.examples) : []
      };
      
      const response = await fetch('/api/tools/test', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(testData),
      });
      
      const data = await response.json();
      
      if (!response.ok) {
        throw new Error(data.message || `HTTP error! status: ${response.status}`);
      }
      
      setTestResult(data);
    } catch (error) {
      console.error('Error testing tool:', error);
      setError(error.message || 'Failed to test tool. Please try again.');
    } finally {
      setTestLoading(false);
    }
  };

  if (loading && tools.length === 0) {
    return (
      <Box sx={{ display: 'flex', justifyContent: 'center', mt: 4 }}>
        <CircularProgress />
      </Box>
    );
  }

  return (
    <Box sx={{ maxWidth: '1200px', mx: 'auto', p: 2 }}>
      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 3 }}>
        <Typography variant="h4" component="h1">
          Custom Tools
        </Typography>
        
        <Button
          variant="contained"
          color="primary"
          startIcon={<AddIcon />}
          onClick={() => handleOpenDialog()}
        >
          Add Tool
        </Button>
      </Box>
      
      {error && (
        <Alert severity="error" sx={{ mb: 3 }} onClose={() => setError(null)}>
          {error}
        </Alert>
      )}
      
      {tools.length === 0 ? (
        <Paper sx={{ p: 4, textAlign: 'center' }}>
          <Typography variant="h6" color="text.secondary" gutterBottom>
            No Custom Tools Yet
          </Typography>
          <Typography variant="body1" color="text.secondary" paragraph>
            Create your first custom tool to extend the system's capabilities.
          </Typography>
          <Button
            variant="outlined"
            startIcon={<AddIcon />}
            onClick={() => handleOpenDialog()}
          >
            Create Tool
          </Button>
        </Paper>
      ) : (
        <Grid container spacing={3}>
          {tools.map((tool) => (
            <Grid item xs={12} md={6} lg={4} key={tool.id}>
              <Card variant="outlined">
                <CardContent>
                  <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start' }}>
                    <Box sx={{ display: 'flex', alignItems: 'center', mb: 1 }}>
                      <BuildIcon color="primary" sx={{ mr: 1 }} />
                      <Typography variant="h6" component="h2">
                        {tool.name}
                      </Typography>
                    </Box>
                    
                    <Box>
                      <Tooltip title="Edit">
                        <IconButton 
                          size="small" 
                          onClick={() => handleOpenDialog(tool)}
                          aria-label="edit"
                        >
                          <EditIcon fontSize="small" />
                        </IconButton>
                      </Tooltip>
                      <Tooltip title="Delete">
                        <IconButton 
                          size="small" 
                          onClick={() => handleDeleteTool(tool.id)}
                          aria-label="delete"
                        >
                          <DeleteIcon fontSize="small" />
                        </IconButton>
                      </Tooltip>
                    </Box>
                  </Box>
                  
                  <Typography variant="body2" color="text.secondary" paragraph>
                    {tool.description}
                  </Typography>
                  
                  {tool.parameters && Object.keys(tool.parameters).length > 0 && (
                    <Box sx={{ mb: 1 }}>
                      <Typography variant="caption" color="text.secondary">
                        Parameters:
                      </Typography>
                      <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 0.5, mt: 0.5 }}>
                        {Object.keys(tool.parameters).map((param) => (
                          <Chip 
                            key={param} 
                            label={param} 
                            size="small" 
                            variant="outlined" 
                          />
                        ))}
                      </Box>
                    </Box>
                  )}
                </CardContent>
                <CardActions>
                  <Button 
                    size="small" 
                    startIcon={<PlayArrowIcon />}
                    onClick={() => handleOpenDialog(tool)}
                  >
                    Test Tool
                  </Button>
                </CardActions>
              </Card>
            </Grid>
          ))}
        </Grid>
      )}
      
      {/* Add/Edit Tool Dialog */}
      <Dialog 
        open={openDialog} 
        onClose={handleCloseDialog}
        maxWidth="md"
        fullWidth
      >
        <DialogTitle>
          {editingTool ? `Edit Tool: ${editingTool.name}` : 'Create New Tool'}
        </DialogTitle>
        <DialogContent dividers>
          {error && (
            <Alert severity="error" sx={{ mb: 2 }} onClose={() => setError(null)}>
              {error}
            </Alert>
          )}
          
          <TextField
            fullWidth
            margin="normal"
            label="Tool Name"
            name="name"
            value={formData.name}
            onChange={handleInputChange}
            required
          />
          
          <TextField
            fullWidth
            margin="normal"
            label="Description"
            name="description"
            value={formData.description}
            onChange={handleInputChange}
            multiline
            rows={2}
            required
          />
          
          <Typography variant="subtitle1" sx={{ mt: 2, mb: 1 }}>
            Tool Code
          </Typography>
          <Paper variant="outlined" sx={{ p: 1 }}>
            <TextField
              fullWidth
              name="code"
              value={formData.code}
              onChange={handleInputChange}
              multiline
              rows={10}
              variant="standard"
              InputProps={{
                disableUnderline: true,
                style: { fontFamily: 'monospace' }
              }}
              required
            />
          </Paper>
          
          <Typography variant="subtitle1" sx={{ mt: 2, mb: 1 }}>
            Parameters (JSON)
          </Typography>
          <Paper variant="outlined" sx={{ p: 1 }}>
            <TextField
              fullWidth
              name="parameters"
              value={formData.parameters}
              onChange={handleInputChange}
              multiline
              rows={5}
              variant="standard"
              InputProps={{
                disableUnderline: true,
                style: { fontFamily: 'monospace' }
              }}
            />
          </Paper>
          
          <Typography variant="subtitle1" sx={{ mt: 2, mb: 1 }}>
            Examples (JSON)
          </Typography>
          <Paper variant="outlined" sx={{ p: 1 }}>
            <TextField
              fullWidth
              name="examples"
              value={formData.examples}
              onChange={handleInputChange}
              multiline
              rows={5}
              variant="standard"
              InputProps={{
                disableUnderline: true,
                style: { fontFamily: 'monospace' }
              }}
            />
          </Paper>
          
          {testResult && (
            <Box sx={{ mt: 3 }}>
              <Typography variant="subtitle1" gutterBottom>
                Test Results:
              </Typography>
              <Paper variant="outlined" sx={{ p: 2, bgcolor: testResult.success ? 'success.light' : 'error.light' }}>
                <Typography variant="subtitle2">
                  {testResult.success ? 'Success' : 'Error'}
                </Typography>
                <Typography variant="body2" sx={{ mt: 1, whiteSpace: 'pre-wrap' }}>
                  {testResult.message}
                </Typography>
                {testResult.result !== undefined && (
                  <Box sx={{ mt: 2 }}>
                    <Typography variant="subtitle2">Result:</Typography>
                    <SyntaxHighlighter
                      language="javascript"
                      style={vscDarkPlus}
                      customStyle={{ borderRadius: '4px' }}
                    >
                      {JSON.stringify(testResult.result, null, 2)}
                    </SyntaxHighlighter>
                  </Box>
                )}
              </Paper>
            </Box>
          )}
        </DialogContent>
        <DialogActions>
          <Button onClick={handleCloseDialog}>Cancel</Button>
          <Button 
            onClick={handleTestTool} 
            color="info" 
            disabled={testLoading}
            startIcon={testLoading ? <CircularProgress size={20} /> : <PlayArrowIcon />}
          >
            Test
          </Button>
          <Button 
            onClick={handleSubmit} 
            color="primary" 
            disabled={loading}
            variant="contained"
          >
            {editingTool ? 'Update' : 'Create'}
          </Button>
        </DialogActions>
      </Dialog>
    </Box>
  );
};

export default Tools;
