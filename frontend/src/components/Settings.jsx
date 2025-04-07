import React, { useState, useEffect } from 'react';
import { Box, Typography, Paper, Tabs, Tab, TextField, Button, Switch, FormControlLabel, 
  Select, MenuItem, FormControl, InputLabel, Divider, Alert, CircularProgress } from '@mui/material';
import SaveIcon from '@mui/icons-material/Save';

const Settings = () => {
  const [activeTab, setActiveTab] = useState(0);
  const [loading, setLoading] = useState(false);
  const [saveStatus, setSaveStatus] = useState(null);
  const [generalSettings, setGeneralSettings] = useState({
    apiBaseUrl: '',
    llmModel: '',
    embeddingModel: '',
    debugMode: false
  });
  const [securitySettings, setSecuritySettings] = useState({
    apiKey: '',
    masterKey: '',
    secretKey: ''
  });
  const [databaseSettings, setDatabaseSettings] = useState({
    databaseUri: '',
    autoBackup: false,
    backupInterval: 24
  });
  const [uiSettings, setUiSettings] = useState({
    theme: 'light',
    codeTheme: 'vs-dark',
    fontSize: 14,
    showMetadata: true
  });

  useEffect(() => {
    // Fetch settings on component mount
    fetchSettings();
  }, []);

  const fetchSettings = async () => {
    try {
      setLoading(true);
      
      // Fetch general settings
      const generalResponse = await fetch('/api/settings/general');
      if (generalResponse.ok) {
        const data = await generalResponse.json();
        setGeneralSettings(data);
      }
      
      // Fetch security settings (masked)
      const securityResponse = await fetch('/api/settings/security');
      if (securityResponse.ok) {
        const data = await securityResponse.json();
        setSecuritySettings(data);
      }
      
      // Fetch database settings
      const dbResponse = await fetch('/api/settings/database');
      if (dbResponse.ok) {
        const data = await dbResponse.json();
        setDatabaseSettings(data);
      }
      
      // Fetch UI settings
      const uiResponse = await fetch('/api/settings/ui');
      if (uiResponse.ok) {
        const data = await uiResponse.json();
        setUiSettings(data);
      }
    } catch (error) {
      console.error('Error fetching settings:', error);
      setSaveStatus({
        type: 'error',
        message: 'Failed to load settings: ' + error.message
      });
    } finally {
      setLoading(false);
    }
  };

  const handleTabChange = (event, newValue) => {
    setActiveTab(newValue);
  };

  const handleGeneralChange = (e) => {
    const { name, value, checked } = e.target;
    setGeneralSettings({
      ...generalSettings,
      [name]: e.target.type === 'checkbox' ? checked : value
    });
  };

  const handleSecurityChange = (e) => {
    const { name, value } = e.target;
    setSecuritySettings({
      ...securitySettings,
      [name]: value
    });
  };

  const handleDatabaseChange = (e) => {
    const { name, value, checked } = e.target;
    setDatabaseSettings({
      ...databaseSettings,
      [name]: e.target.type === 'checkbox' ? checked : value
    });
  };

  const handleUiChange = (e) => {
    const { name, value, checked } = e.target;
    setUiSettings({
      ...uiSettings,
      [name]: e.target.type === 'checkbox' ? checked : value
    });
  };

  const saveSettings = async () => {
    try {
      setLoading(true);
      setSaveStatus(null);
      
      // Save general settings
      const generalResponse = await fetch('/api/settings/general', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(generalSettings),
      });
      
      if (!generalResponse.ok) {
        throw new Error('Failed to save general settings');
      }
      
      // Save security settings
      const securityResponse = await fetch('/api/settings/security', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(securitySettings),
      });
      
      if (!securityResponse.ok) {
        throw new Error('Failed to save security settings');
      }
      
      // Save database settings
      const dbResponse = await fetch('/api/settings/database', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(databaseSettings),
      });
      
      if (!dbResponse.ok) {
        throw new Error('Failed to save database settings');
      }
      
      // Save UI settings
      const uiResponse = await fetch('/api/settings/ui', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(uiSettings),
      });
      
      if (!uiResponse.ok) {
        throw new Error('Failed to save UI settings');
      }
      
      setSaveStatus({
        type: 'success',
        message: 'Settings saved successfully'
      });
      
      // Reload settings to get any server-side changes
      fetchSettings();
    } catch (error) {
      console.error('Error saving settings:', error);
      setSaveStatus({
        type: 'error',
        message: 'Failed to save settings: ' + error.message
      });
    } finally {
      setLoading(false);
    }
  };

  return (
    <Box sx={{ maxWidth: '1000px', mx: 'auto', p: 2 }}>
      <Typography variant="h4" component="h1" gutterBottom>
        System Settings
      </Typography>
      
      {saveStatus && (
        <Alert 
          severity={saveStatus.type} 
          sx={{ mb: 2 }}
          onClose={() => setSaveStatus(null)}
        >
          {saveStatus.message}
        </Alert>
      )}
      
      <Paper sx={{ mb: 3 }}>
        <Tabs
          value={activeTab}
          onChange={handleTabChange}
          variant="fullWidth"
        >
          <Tab label="General" />
          <Tab label="Security" />
          <Tab label="Database" />
          <Tab label="UI" />
        </Tabs>
      </Paper>
      
      {/* General Settings */}
      {activeTab === 0 && (
        <Paper sx={{ p: 3 }}>
          <Typography variant="h6" gutterBottom>
            General Settings
          </Typography>
          
          <Box sx={{ mb: 3 }}>
            <TextField
              fullWidth
              margin="normal"
              label="API Base URL"
              name="apiBaseUrl"
              value={generalSettings.apiBaseUrl}
              onChange={handleGeneralChange}
              helperText="Base URL for API requests (e.g., https://api.lastwinnersllc.com)"
            />
            
            <TextField
              fullWidth
              margin="normal"
              label="LLM Model"
              name="llmModel"
              value={generalSettings.llmModel}
              onChange={handleGeneralChange}
              helperText="Language model to use (e.g., llama3.2)"
            />
            
            <TextField
              fullWidth
              margin="normal"
              label="Embedding Model"
              name="embeddingModel"
              value={generalSettings.embeddingModel}
              onChange={handleGeneralChange}
              helperText="Embedding model to use (e.g., nomic-embed-text)"
            />
            
            <FormControlLabel
              control={
                <Switch
                  checked={generalSettings.debugMode}
                  onChange={handleGeneralChange}
                  name="debugMode"
                />
              }
              label="Debug Mode"
              sx={{ mt: 2 }}
            />
          </Box>
        </Paper>
      )}
      
      {/* Security Settings */}
      {activeTab === 1 && (
        <Paper sx={{ p: 3 }}>
          <Typography variant="h6" gutterBottom>
            Security Settings
          </Typography>
          
          <Alert severity="info" sx={{ mb: 2 }}>
            API keys and secrets are stored securely and encrypted in the database.
          </Alert>
          
          <Box sx={{ mb: 3 }}>
            <TextField
              fullWidth
              margin="normal"
              label="API Key"
              name="apiKey"
              type="password"
              value={securitySettings.apiKey}
              onChange={handleSecurityChange}
              helperText="API key for external services"
            />
            
            <TextField
              fullWidth
              margin="normal"
              label="Master Key"
              name="masterKey"
              type="password"
              value={securitySettings.masterKey}
              onChange={handleSecurityChange}
              helperText="Master key for encryption (changing this will invalidate existing encrypted data)"
            />
            
            <TextField
              fullWidth
              margin="normal"
              label="Secret Key"
              name="secretKey"
              type="password"
              value={securitySettings.secretKey}
              onChange={handleSecurityChange}
              helperText="Secret key for session management"
            />
          </Box>
        </Paper>
      )}
      
      {/* Database Settings */}
      {activeTab === 2 && (
        <Paper sx={{ p: 3 }}>
          <Typography variant="h6" gutterBottom>
            Database Settings
          </Typography>
          
          <Box sx={{ mb: 3 }}>
            <TextField
              fullWidth
              margin="normal"
              label="Database URI"
              name="databaseUri"
              value={databaseSettings.databaseUri}
              onChange={handleDatabaseChange}
              helperText="Database connection URI (e.g., sqlite:///ai_agent.db)"
            />
            
            <FormControlLabel
              control={
                <Switch
                  checked={databaseSettings.autoBackup}
                  onChange={handleDatabaseChange}
                  name="autoBackup"
                />
              }
              label="Automatic Backup"
              sx={{ mt: 2, display: 'block' }}
            />
            
            {databaseSettings.autoBackup && (
              <TextField
                margin="normal"
                label="Backup Interval (hours)"
                name="backupInterval"
                type="number"
                value={databaseSettings.backupInterval}
                onChange={handleDatabaseChange}
                InputProps={{ inputProps: { min: 1, max: 168 } }}
              />
            )}
          </Box>
        </Paper>
      )}
      
      {/* UI Settings */}
      {activeTab === 3 && (
        <Paper sx={{ p: 3 }}>
          <Typography variant="h6" gutterBottom>
            UI Settings
          </Typography>
          
          <Box sx={{ mb: 3 }}>
            <FormControl fullWidth margin="normal">
              <InputLabel id="theme-label">Theme</InputLabel>
              <Select
                labelId="theme-label"
                name="theme"
                value={uiSettings.theme}
                label="Theme"
                onChange={handleUiChange}
              >
                <MenuItem value="light">Light</MenuItem>
                <MenuItem value="dark">Dark</MenuItem>
                <MenuItem value="system">System Default</MenuItem>
              </Select>
            </FormControl>
            
            <FormControl fullWidth margin="normal">
              <InputLabel id="code-theme-label">Code Editor Theme</InputLabel>
              <Select
                labelId="code-theme-label"
                name="codeTheme"
                value={uiSettings.codeTheme}
                label="Code Editor Theme"
                onChange={handleUiChange}
              >
                <MenuItem value="vs-light">Light</MenuItem>
                <MenuItem value="vs-dark">Dark</MenuItem>
                <MenuItem value="hc-black">High Contrast</MenuItem>
              </Select>
            </FormControl>
            
            <TextField
              margin="normal"
              label="Font Size"
              name="fontSize"
              type="number"
              value={uiSettings.fontSize}
              onChange={handleUiChange}
              InputProps={{ inputProps: { min: 10, max: 24 } }}
            />
            
            <FormControlLabel
              control={
                <Switch
                  checked={uiSettings.showMetadata}
                  onChange={handleUiChange}
                  name="showMetadata"
                />
              }
              label="Show Metadata in Chat"
              sx={{ mt: 2, display: 'block' }}
            />
          </Box>
        </Paper>
      )}
      
      <Box sx={{ mt: 3, display: 'flex', justifyContent: 'flex-end' }}>
        <Button
          variant="contained"
          color="primary"
          startIcon={loading ? <CircularProgress size={24} /> : <SaveIcon />}
          onClick={saveSettings}
          disabled={loading}
        >
          Save Settings
        </Button>
      </Box>
    </Box>
  );
};

export default Settings;
