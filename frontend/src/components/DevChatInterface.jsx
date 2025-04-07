import React, { useState, useEffect } from 'react';
import { Box, Typography, Paper, CircularProgress, Button } from '@mui/material';
import MonacoEditor from 'react-monaco-editor';

const DevChatInterface = () => {
  const [query, setQuery] = useState('');
  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(false);
  const [codeMap, setCodeMap] = useState(null);
  const [stats, setStats] = useState(null);

  useEffect(() => {
    // Fetch code stats on component mount
    fetchStats();
  }, []);

  const fetchStats = async () => {
    try {
      const response = await fetch('/api/dev-chat/stats');
      if (response.ok) {
        const data = await response.json();
        setStats(data);
      }
    } catch (error) {
      console.error('Error fetching stats:', error);
    }
  };

  const fetchCodeMap = async () => {
    try {
      setLoading(true);
      const response = await fetch('/api/dev-chat/map');
      if (response.ok) {
        const data = await response.json();
        setCodeMap(data);
      }
    } catch (error) {
      console.error('Error fetching code map:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!query.trim()) return;

    try {
      setLoading(true);
      const response = await fetch('/api/dev-chat/query', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ query }),
      });

      if (response.ok) {
        const data = await response.json();
        setResult(data);
      } else {
        throw new Error('Failed to process query');
      }
    } catch (error) {
      console.error('Error processing query:', error);
      setResult({ error: error.message });
    } finally {
      setLoading(false);
    }
  };

  const renderResult = () => {
    if (!result) return null;

    if (result.error) {
      return (
        <Paper sx={{ p: 2, mt: 2, bgcolor: 'error.light' }}>
          <Typography color="error">{result.error}</Typography>
        </Paper>
      );
    }

    switch (result.type) {
      case 'impact_analysis':
        return (
          <Paper sx={{ p: 2, mt: 2 }}>
            <Typography variant="h6">Impact Analysis for {result.file}</Typography>
            <Typography variant="body1" sx={{ mt: 1 }}>
              Total impact: {result.impact.total_impact_count} files
            </Typography>
            
            <Typography variant="subtitle1" sx={{ mt: 2 }}>Direct Dependents:</Typography>
            {result.impact.direct_dependents.length > 0 ? (
              <ul>
                {result.impact.direct_dependents.map((dep, i) => (
                  <li key={i}>{dep.source}</li>
                ))}
              </ul>
            ) : (
              <Typography variant="body2">No direct dependents</Typography>
            )}
            
            <Typography variant="subtitle1" sx={{ mt: 2 }}>Transitive Dependents:</Typography>
            {result.impact.transitive_dependents.length > 0 ? (
              <ul>
                {result.impact.transitive_dependents.map((dep, i) => (
                  <li key={i}>{dep.source} (via {dep.via})</li>
                ))}
              </ul>
            ) : (
              <Typography variant="body2">No transitive dependents</Typography>
            )}
          </Paper>
        );
      
      case 'database_interactions':
        return (
          <Paper sx={{ p: 2, mt: 2 }}>
            <Typography variant="h6">Database Interactions</Typography>
            {result.functions.length > 0 ? (
              <ul>
                {result.functions.map((func, i) => (
                  <li key={i}>
                    {func.file}: 
                    {func.class ? ` ${func.class}.${func.method}` : ` ${func.function}`} 
                    (line {func.lineno})
                  </li>
                ))}
              </ul>
            ) : (
              <Typography variant="body2">No database interactions found</Typography>
            )}
          </Paper>
        );
      
      case 'function_calls':
        return (
          <Paper sx={{ p: 2, mt: 2 }}>
            <Typography variant="h6">Function Calls for {result.function}</Typography>
            {result.callers.length > 0 ? (
              <ul>
                {result.callers.map((caller, i) => (
                  <li key={i}>{caller.source}</li>
                ))}
              </ul>
            ) : (
              <Typography variant="body2">No callers found</Typography>
            )}
          </Paper>
        );
      
      case 'semantic_search':
        return (
          <Paper sx={{ p: 2, mt: 2 }}>
            <Typography variant="h6">Search Results</Typography>
            {result.results.length > 0 ? (
              result.results.map((item, i) => (
                <Box key={i} sx={{ mt: 2, p: 1, border: 1, borderColor: 'grey.300', borderRadius: 1 }}>
                  <Typography variant="subtitle1">
                    {item.metadata.type === 'file' ? 'File: ' : item.metadata.type === 'class' ? 'Class: ' : 'Function: '}
                    {item.metadata.name || item.metadata.path}
                  </Typography>
                  <Typography variant="body2" sx={{ mt: 1, whiteSpace: 'pre-wrap' }}>
                    {item.document}
                  </Typography>
                </Box>
              ))
            ) : (
              <Typography variant="body2">No results found</Typography>
            )}
          </Paper>
        );
      
      default:
        return (
          <Paper sx={{ p: 2, mt: 2 }}>
            <Typography variant="h6">Result</Typography>
            <pre>{JSON.stringify(result, null, 2)}</pre>
          </Paper>
        );
    }
  };

  return (
    <Box sx={{ maxWidth: '1000px', mx: 'auto', p: 2 }}>
      <Typography variant="h4" component="h1" gutterBottom>
        DevChat Code Intelligence
      </Typography>
      
      {stats && (
        <Paper sx={{ p: 2, mb: 3 }}>
          <Typography variant="h6" gutterBottom>
            Codebase Statistics
          </Typography>
          <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 2 }}>
            <Box sx={{ flex: '1 1 auto', minWidth: '120px' }}>
              <Typography variant="body2" color="text.secondary">Files</Typography>
              <Typography variant="h5">{stats.files}</Typography>
            </Box>
            <Box sx={{ flex: '1 1 auto', minWidth: '120px' }}>
              <Typography variant="body2" color="text.secondary">Graph Nodes</Typography>
              <Typography variant="h5">{stats.nodes}</Typography>
            </Box>
            <Box sx={{ flex: '1 1 auto', minWidth: '120px' }}>
              <Typography variant="body2" color="text.secondary">Graph Edges</Typography>
              <Typography variant="h5">{stats.edges}</Typography>
            </Box>
            <Box sx={{ flex: '1 1 auto', minWidth: '120px' }}>
              <Typography variant="body2" color="text.secondary">Vector Items</Typography>
              <Typography variant="h5">{stats.vector_items}</Typography>
            </Box>
          </Box>
          <Button 
            variant="outlined" 
            sx={{ mt: 2 }} 
            onClick={fetchCodeMap}
            disabled={loading}
          >
            View Code Map
          </Button>
        </Paper>
      )}
      
      <Paper sx={{ p: 2, mb: 3 }}>
        <Typography variant="h6" gutterBottom>
          Query the Codebase
        </Typography>
        <Typography variant="body2" color="text.secondary" paragraph>
          Ask questions about the codebase structure, dependencies, and functionality.
        </Typography>
        
        <form onSubmit={handleSubmit}>
          <Box sx={{ mb: 2 }}>
            <MonacoEditor
              width="100%"
              height="100px"
              language="plaintext"
              theme="vs-light"
              value={query}
              options={{
                minimap: { enabled: false },
                lineNumbers: 'off',
                scrollBeyondLastLine: false,
                wordWrap: 'on'
              }}
              onChange={setQuery}
            />
          </Box>
          
          <Button 
            type="submit" 
            variant="contained" 
            disabled={loading || !query.trim()}
          >
            {loading ? <CircularProgress size={24} /> : 'Submit Query'}
          </Button>
        </form>
        
        <Box sx={{ mt: 2 }}>
          <Typography variant="subtitle2" gutterBottom>
            Example queries:
          </Typography>
          <ul>
            <li>What modules are impacted if I change auth.py?</li>
            <li>Show me all functions that write to the database.</li>
            <li>Where is the function process_query used?</li>
            <li>How does the RAG memory system work?</li>
          </ul>
        </Box>
      </Paper>
      
      {renderResult()}
      
      {codeMap && (
        <Paper sx={{ p: 2, mt: 3 }}>
          <Typography variant="h6" gutterBottom>
            Code Map
          </Typography>
          <Typography variant="body2" paragraph>
            {codeMap.nodes.length} nodes and {codeMap.links.length} relationships found.
          </Typography>
          <Box sx={{ maxHeight: '400px', overflow: 'auto' }}>
            <pre>{JSON.stringify(codeMap, null, 2)}</pre>
          </Box>
        </Paper>
      )}
    </Box>
  );
};

export default DevChatInterface;
