import React, { useState, useEffect } from 'react';
import { Box, Typography, Paper, Grid, Card, CardContent, CardHeader, Divider, Button, CircularProgress } from '@mui/material';
import MonacoEditor from 'react-monaco-editor';

const CodeEditor = ({ value, onChange, language = 'javascript', height = '400px', readOnly = false }) => {
  const options = {
    selectOnLineNumbers: true,
    readOnly: readOnly,
    minimap: { enabled: true },
    scrollBeyondLastLine: false,
    automaticLayout: true
  };

  return (
    <MonacoEditor
      width="100%"
      height={height}
      language={language}
      theme="vs-dark"
      value={value}
      options={options}
      onChange={onChange}
    />
  );
};

export default CodeEditor;
