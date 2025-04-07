import React, { useState, useEffect } from 'react';
import { Box, Typography, Paper, Tabs, Tab, Table, TableBody, TableCell, TableContainer, 
  TableHead, TableRow, CircularProgress, Chip, Button, Dialog, DialogTitle, 
  DialogContent, DialogContentText, DialogActions } from '@mui/material';
import RefreshIcon from '@mui/icons-material/Refresh';
import DownloadIcon from '@mui/icons-material/Download';

const Logging = () => {
  const [activeTab, setActiveTab] = useState(0);
  const [logs, setLogs] = useState([]);
  const [loading, setLoading] = useState(true);
  const [detailDialog, setDetailDialog] = useState({
    open: false,
    log: null
  });

  useEffect(() => {
    fetchLogs();
    // Set up polling for logs every 10 seconds
    const interval = setInterval(fetchLogs, 10000);
    return () => clearInterval(interval);
  }, [activeTab]);

  const fetchLogs = async () => {
    try {
      setLoading(true);
      const logTypes = ['system', 'api', 'interpreter', 'database'];
      const logType = logTypes[activeTab];
      
      const response = await fetch(`/api/logs/${logType}`);
      if (!response.ok) {
        throw new Error(`Error: ${response.statusText}`);
      }
      
      const data = await response.json();
      setLogs(data.logs || []);
    } catch (error) {
      console.error('Error fetching logs:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleTabChange = (event, newValue) => {
    setActiveTab(newValue);
  };

  const handleRefresh = () => {
    fetchLogs();
  };

  const handleOpenDetail = (log) => {
    setDetailDialog({
      open: true,
      log
    });
  };

  const handleCloseDetail = () => {
    setDetailDialog({
      open: false,
      log: null
    });
  };

  const handleDownloadLogs = () => {
    const logTypes = ['system', 'api', 'interpreter', 'database'];
    const logType = logTypes[activeTab];
    
    // Create a download link
    const element = document.createElement('a');
    const file = new Blob(
      [JSON.stringify(logs, null, 2)], 
      {type: 'application/json'}
    );
    element.href = URL.createObjectURL(file);
    element.download = `${logType}_logs_${new Date().toISOString()}.json`;
    document.body.appendChild(element);
    element.click();
    document.body.removeChild(element);
  };

  const getLevelColor = (level) => {
    switch (level.toLowerCase()) {
      case 'error':
        return 'error';
      case 'warning':
        return 'warning';
      case 'info':
        return 'info';
      case 'debug':
        return 'default';
      default:
        return 'default';
    }
  };

  const formatTimestamp = (timestamp) => {
    return new Date(timestamp).toLocaleString();
  };

  return (
    <Box sx={{ maxWidth: '1000px', mx: 'auto', p: 2 }}>
      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 2 }}>
        <Typography variant="h4" component="h1">
          System Logs
        </Typography>
        <Box>
          <Button 
            variant="outlined" 
            startIcon={<DownloadIcon />} 
            onClick={handleDownloadLogs}
            sx={{ mr: 1 }}
          >
            Download
          </Button>
          <Button 
            variant="contained" 
            startIcon={<RefreshIcon />} 
            onClick={handleRefresh}
          >
            Refresh
          </Button>
        </Box>
      </Box>

      <Paper sx={{ mb: 3 }}>
        <Tabs
          value={activeTab}
          onChange={handleTabChange}
          variant="fullWidth"
        >
          <Tab label="System" />
          <Tab label="API" />
          <Tab label="Interpreter" />
          <Tab label="Database" />
        </Tabs>
      </Paper>

      {loading ? (
        <Box sx={{ display: 'flex', justifyContent: 'center', my: 4 }}>
          <CircularProgress />
        </Box>
      ) : logs.length === 0 ? (
        <Paper sx={{ p: 3, textAlign: 'center' }}>
          <Typography variant="body1">
            No logs available for this category.
          </Typography>
        </Paper>
      ) : (
        <TableContainer component={Paper}>
          <Table sx={{ minWidth: 650 }}>
            <TableHead>
              <TableRow>
                <TableCell>Timestamp</TableCell>
                <TableCell>Level</TableCell>
                <TableCell>Source</TableCell>
                <TableCell>Message</TableCell>
                <TableCell>Actions</TableCell>
              </TableRow>
            </TableHead>
            <TableBody>
              {logs.map((log, index) => (
                <TableRow key={index}>
                  <TableCell>{formatTimestamp(log.timestamp)}</TableCell>
                  <TableCell>
                    <Chip 
                      label={log.level} 
                      color={getLevelColor(log.level)} 
                      size="small" 
                    />
                  </TableCell>
                  <TableCell>{log.source}</TableCell>
                  <TableCell>
                    {log.message.length > 100 
                      ? `${log.message.substring(0, 100)}...` 
                      : log.message}
                  </TableCell>
                  <TableCell>
                    <Button 
                      variant="outlined" 
                      size="small" 
                      onClick={() => handleOpenDetail(log)}
                    >
                      Details
                    </Button>
                  </TableCell>
                </TableRow>
              ))}
            </TableBody>
          </Table>
        </TableContainer>
      )}

      {/* Log Detail Dialog */}
      <Dialog
        open={detailDialog.open}
        onClose={handleCloseDetail}
        maxWidth="md"
        fullWidth
      >
        <DialogTitle>
          Log Details
        </DialogTitle>
        <DialogContent>
          {detailDialog.log && (
            <>
              <Box sx={{ mb: 2 }}>
                <Typography variant="subtitle2">Timestamp:</Typography>
                <Typography variant="body1">{formatTimestamp(detailDialog.log.timestamp)}</Typography>
              </Box>
              
              <Box sx={{ mb: 2 }}>
                <Typography variant="subtitle2">Level:</Typography>
                <Chip 
                  label={detailDialog.log.level} 
                  color={getLevelColor(detailDialog.log.level)} 
                  size="small" 
                />
              </Box>
              
              <Box sx={{ mb: 2 }}>
                <Typography variant="subtitle2">Source:</Typography>
                <Typography variant="body1">{detailDialog.log.source}</Typography>
              </Box>
              
              <Box sx={{ mb: 2 }}>
                <Typography variant="subtitle2">Message:</Typography>
                <Paper sx={{ p: 2, backgroundColor: 'grey.100' }}>
                  <Typography 
                    variant="body2" 
                    component="pre" 
                    sx={{ 
                      whiteSpace: 'pre-wrap', 
                      wordBreak: 'break-word',
                      fontFamily: 'monospace'
                    }}
                  >
                    {detailDialog.log.message}
                  </Typography>
                </Paper>
              </Box>
              
              {detailDialog.log.metadata && (
                <Box sx={{ mb: 2 }}>
                  <Typography variant="subtitle2">Metadata:</Typography>
                  <Paper sx={{ p: 2, backgroundColor: 'grey.100' }}>
                    <Typography 
                      variant="body2" 
                      component="pre" 
                      sx={{ 
                        whiteSpace: 'pre-wrap', 
                        wordBreak: 'break-word',
                        fontFamily: 'monospace'
                      }}
                    >
                      {JSON.stringify(detailDialog.log.metadata, null, 2)}
                    </Typography>
                  </Paper>
                </Box>
              )}
            </>
          )}
        </DialogContent>
        <DialogActions>
          <Button onClick={handleCloseDetail}>Close</Button>
        </DialogActions>
      </Dialog>
    </Box>
  );
};

export default Logging;
