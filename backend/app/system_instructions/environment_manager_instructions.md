# Environment Manager System Instructions

## Overview

The Environment Manager is a critical security component of the AI Agent System that handles API keys, secrets, and environment variables. It provides a secure way to store, retrieve, and manage sensitive information needed by the system and custom tools.

This document provides detailed instructions on how to effectively use and manage the Environment Manager.

## Core Functionality

The Environment Manager provides the following key capabilities:

1. **Secret Storage**: Securely store API keys and sensitive information
2. **Variable Management**: Set, retrieve, and update environment variables
3. **Access Control**: Manage permissions for accessing sensitive data
4. **Encryption**: Encrypt sensitive information at rest
5. **Integration**: Provide secure access to secrets for tools and components

## Managing Environment Variables

### Setting Variables

To set an environment variable:

Through the Settings interface:
1. Navigate to the Security tab in Settings
2. Use the Environment Variables section to add or update variables

Through the Chat interface:
```
Set environment variable [KEY] to [VALUE]
```

For example:
```
Set environment variable API_KEY to "abc123xyz789"
```

The system will:
1. Store the variable securely
2. Encrypt sensitive values
3. Make the variable available to system components

### Retrieving Variables

To retrieve an environment variable:

Through the Settings interface:
1. Navigate to the Security tab in Settings
2. View the Environment Variables section (sensitive values will be masked)

Through the Chat interface:
```
Get environment variable [KEY]
```

For example:
```
Get environment variable API_KEY
```

The system will:
1. Check if you have permission to access the variable
2. Return the value (masked if sensitive)
3. For security reasons, full values of sensitive variables may not be displayed

### Updating Variables

To update an existing environment variable:

```
Update environment variable [KEY] to [NEW_VALUE]
```

For example:
```
Update environment variable API_KEY to "new_api_key_value"
```

### Deleting Variables

To delete an environment variable:

```
Delete environment variable [KEY]
```

For example:
```
Delete environment variable DEPRECATED_API_KEY
```

## Variable Types and Security Levels

The Environment Manager supports different types of variables with varying security levels:

### Public Variables
- Not encrypted
- Accessible by all system components
- Typically used for non-sensitive configuration
- Example: `LOG_LEVEL`, `DEFAULT_LANGUAGE`

### Protected Variables
- Encrypted at rest
- Accessible by authorized components
- Typically used for semi-sensitive information
- Example: `DATABASE_URI`, `SERVICE_ENDPOINT`

### Secret Variables
- Strongly encrypted at rest
- Accessible only by specific components with explicit permission
- Used for highly sensitive information
- Example: `API_KEY`, `ENCRYPTION_KEY`, `AUTH_TOKEN`

To specify a security level when setting a variable:

```
Set [public/protected/secret] environment variable [KEY] to [VALUE]
```

For example:
```
Set secret environment variable PAYMENT_API_KEY to "sk_live_123456789"
```

## Using Environment Variables in Tools

When creating custom tools, you can securely access environment variables:

```python
import os

def my_tool_function():
    # Securely access an environment variable
    api_key = os.environ.get("MY_API_KEY")
    
    if not api_key:
        return {"error": "API key not configured"}
    
    # Use the API key securely
    # ...
```

Best practices for using environment variables in tools:

1. Always check if the variable exists before using it
2. Provide helpful error messages when required variables are missing
3. Never log or expose sensitive variables
4. Request only the minimum required permissions

## Advanced Features

### Variable Categories

You can organize variables into categories:

```
Set environment variable [KEY] in category [CATEGORY] to [VALUE]
```

For example:
```
Set environment variable API_KEY in category PAYMENT_PROCESSOR to "sk_live_123456789"
```

To list variables in a category:

```
List environment variables in category [CATEGORY]
```

### Temporary Variables

You can set variables that expire after a certain time:

```
Set temporary environment variable [KEY] to [VALUE] for [DURATION]
```

For example:
```
Set temporary environment variable SESSION_TOKEN to "abc123" for 1 hour
```

### Variable Descriptions

You can add descriptions to variables for better documentation:

```
Set environment variable [KEY] to [VALUE] with description "[DESCRIPTION]"
```

For example:
```
Set environment variable OPENAI_API_KEY to "sk-123456" with description "API key for OpenAI services"
```

## Security Best Practices

1. **Principle of least privilege**: Only request access to variables your tool actually needs
2. **Regular rotation**: Periodically update sensitive keys and tokens
3. **Avoid hardcoding**: Never hardcode secrets in tool code
4. **Use specific names**: Choose descriptive, specific variable names
5. **Add descriptions**: Document what each variable is used for
6. **Audit regularly**: Review environment variables periodically and remove unused ones

## Troubleshooting

If you encounter issues with the Environment Manager:

1. **Access denied**: Verify you have the necessary permissions
2. **Variable not found**: Check if the variable name is correct (names are case-sensitive)
3. **Encryption issues**: Contact the system administrator if you suspect encryption problems
4. **Tool can't access variable**: Ensure the tool has the required permissions

## Examples

### Example 1: Setting up API access for a weather tool

```
Set secret environment variable WEATHER_API_KEY to "abcdef123456" with description "API key for weather service"
```

Then in the weather tool code:

```python
import os
import requests

def get_weather(location):
    api_key = os.environ.get("WEATHER_API_KEY")
    if not api_key:
        return {"error": "Weather API key not configured"}
    
    url = f"https://api.weather.com/forecast?key={api_key}&location={location}"
    response = requests.get(url)
    # Process response...
```

### Example 2: Managing database credentials

```
Set protected environment variable DATABASE_URI to "postgresql://user:password@localhost:5432/mydb"
```

Then in the database connection code:

```python
import os
from sqlalchemy import create_engine

def get_database_connection():
    db_uri = os.environ.get("DATABASE_URI")
    if not db_uri:
        raise Exception("Database URI not configured")
    
    engine = create_engine(db_uri)
    return engine.connect()
```

### Example 3: Setting temporary credentials

```
Set temporary environment variable AUTH_TOKEN to "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..." for 30 minutes
```

Then in the authentication code:

```python
import os

def verify_auth():
    token = os.environ.get("AUTH_TOKEN")
    if not token:
        return {"authenticated": False, "error": "No auth token found"}
    
    # Verify token...
    return {"authenticated": True}
```
