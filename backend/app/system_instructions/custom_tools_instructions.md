# Custom Tools System Instructions

## Overview

The Custom Tools System is a powerful component of the AI Agent System that allows users to extend the system's capabilities by creating, managing, and executing custom tools. These tools can perform specialized functions, integrate with external services, and automate complex tasks.

This document provides detailed instructions on how to effectively use and manage the Custom Tools System.

## Core Functionality

The Custom Tools System provides the following key capabilities:

1. **Tool Creation**: Define new tools with custom functionality
2. **Tool Management**: Organize, edit, and delete existing tools
3. **Tool Execution**: Run tools with specific parameters
4. **Tool Discovery**: Find and learn about available tools
5. **Context-Aware Integration**: Use tools within the chat interface seamlessly

## Creating Custom Tools

### Through the Tools Interface

The most straightforward way to create a custom tool is through the dedicated Tools interface:

1. Navigate to the Tools section in the UI
2. Click "Add Tool" button
3. Fill in the required information:
   - **Name**: A unique, descriptive name for the tool
   - **Description**: Clear explanation of what the tool does
   - **Code**: Python code that implements the tool's functionality
   - **Parameters**: JSON definition of input parameters
   - **Examples**: Sample inputs and expected outputs

### Through the Chat Interface

You can also create tools directly through the chat:

```
Create a new tool called [name] that [description of functionality]
```

The Chat Agent will guide you through the process of defining the tool's parameters and implementation.

## Tool Definition Components

### Tool Name

- Must be unique across the system
- Should be descriptive and indicate the tool's purpose
- Use camelCase or snake_case for consistency
- Examples: `weatherForecast`, `currency_converter`, `imageGenerator`

### Description

- Clearly explain what the tool does
- Mention required inputs and expected outputs
- Include any limitations or requirements
- Will be shown to users when they browse available tools

### Code Implementation

- Written in Python
- Must include a main function that serves as the entry point
- Should handle errors gracefully
- Can import standard libraries and installed packages
- Example:

```python
def calculate_mortgage(principal, interest_rate, years):
    """
    Calculate monthly mortgage payment
    
    Args:
        principal (float): Loan amount in dollars
        interest_rate (float): Annual interest rate (percentage)
        years (int): Loan term in years
        
    Returns:
        float: Monthly payment amount
    """
    monthly_rate = interest_rate / 100 / 12
    months = years * 12
    payment = principal * (monthly_rate * (1 + monthly_rate)**months) / ((1 + monthly_rate)**months - 1)
    return round(payment, 2)
```

### Parameters Definition

- JSON object defining expected parameters
- Each parameter needs:
  - Type (string, number, boolean, object, array)
  - Description
  - Optional: default value, constraints
- Example:

```json
{
  "principal": {
    "type": "number",
    "description": "Loan amount in dollars",
    "minimum": 1000
  },
  "interest_rate": {
    "type": "number",
    "description": "Annual interest rate (percentage)",
    "minimum": 0.1,
    "maximum": 30
  },
  "years": {
    "type": "integer",
    "description": "Loan term in years",
    "minimum": 1,
    "maximum": 50
  }
}
```

### Examples

- Provide sample inputs and expected outputs
- Helps users understand how to use the tool
- Used for testing the tool implementation
- Example:

```json
[
  {
    "principal": 300000,
    "interest_rate": 4.5,
    "years": 30,
    "result": 1520.06
  },
  {
    "principal": 200000,
    "interest_rate": 3.75,
    "years": 15,
    "result": 1454.28
  }
]
```

## Managing Tools

### Editing Tools

To modify an existing tool:

1. Navigate to the Tools section
2. Find the tool you want to edit
3. Click the "Edit" button
4. Make your changes to any component
5. Test the tool to ensure it works correctly
6. Save your changes

Through chat:
```
Edit the tool [tool_name]
```

### Testing Tools

Before saving a tool, you should test it:

1. In the tool editor, click "Test"
2. The system will run the tool with your example inputs
3. Verify the outputs match your expectations
4. Fix any errors or discrepancies

### Deleting Tools

To remove a tool:

1. Navigate to the Tools section
2. Find the tool you want to delete
3. Click the "Delete" button
4. Confirm the deletion

Through chat:
```
Delete the tool [tool_name]
```

## Using Tools

### Through the Chat Interface

The most common way to use tools is through the chat:

```
Use the [tool_name] tool to [task description]
```

or

```
[Specific request that implies using a tool]
```

The Chat Agent will:
1. Recognize the need for the tool
2. Request any missing parameters
3. Execute the tool
4. Present the results

### Direct Tool Execution

For more control, you can directly execute a tool with specific parameters:

```
Execute [tool_name] with parameters: [parameter1=value1, parameter2=value2, ...]
```

### Tool Chaining

You can chain multiple tools together:

```
Use [tool1] to [task1], then use the result with [tool2] to [task2]
```

The system will:
1. Execute the first tool
2. Use its output as input for the second tool
3. Present the final result

## Advanced Features

### Tool Categories

Tools are organized into categories for easier discovery:

- **Data Processing**: Tools for manipulating and analyzing data
- **External Integration**: Tools that connect to external services
- **Utility**: General-purpose helper tools
- **Media**: Tools for handling images, audio, and video
- **Custom**: User-defined categories

To assign a category when creating a tool:

```
Create a new [category] tool called [name] that [description]
```

### Tool Permissions

Tools can have different permission levels:

- **Public**: Available to all users
- **Private**: Available only to the creator
- **Shared**: Available to specific users or groups

To set permissions:

```
Make the [tool_name] tool [public/private/shared with [user/group]]
```

### Tool Versioning

The system maintains versions of tools:

1. Each edit creates a new version
2. You can view the history of changes
3. You can revert to previous versions if needed

To view versions:

```
Show version history for [tool_name]
```

To revert:

```
Revert [tool_name] to version [number]
```

## Best Practices

1. **Start simple**: Begin with basic functionality and expand as needed
2. **Handle errors**: Include error checking and helpful error messages
3. **Document thoroughly**: Provide clear descriptions and examples
4. **Test extensively**: Verify your tool works with various inputs
5. **Use meaningful names**: Make tool and parameter names self-explanatory
6. **Respect limitations**: Be aware of execution time and resource limits
7. **Consider security**: Don't include sensitive information in tool code

## Troubleshooting

If you encounter issues with custom tools:

1. **Syntax errors**: Check your Python code for syntax errors
2. **Parameter mismatches**: Ensure parameter names in code match the JSON definition
3. **Import errors**: Verify all required packages are available
4. **Execution timeouts**: Optimize code for better performance
5. **Unexpected results**: Add debugging print statements to trace execution

## Examples

### Example 1: Simple Calculator Tool

```python
def calculator(operation, a, b):
    """
    Perform basic arithmetic operations
    
    Args:
        operation (str): The operation to perform (add, subtract, multiply, divide)
        a (float): First number
        b (float): Second number
        
    Returns:
        float: Result of the operation
    """
    if operation == "add":
        return a + b
    elif operation == "subtract":
        return a - b
    elif operation == "multiply":
        return a * b
    elif operation == "divide":
        if b == 0:
            return "Error: Division by zero"
        return a / b
    else:
        return "Error: Invalid operation"
```

Parameters:
```json
{
  "operation": {
    "type": "string",
    "description": "The operation to perform",
    "enum": ["add", "subtract", "multiply", "divide"]
  },
  "a": {
    "type": "number",
    "description": "First number"
  },
  "b": {
    "type": "number",
    "description": "Second number"
  }
}
```

### Example 2: Weather Forecast Tool

```python
import requests

def get_weather(location, days=1):
    """
    Get weather forecast for a location
    
    Args:
        location (str): City name or zip code
        days (int): Number of days for forecast (1-7)
        
    Returns:
        dict: Weather forecast information
    """
    api_key = os.environ.get("WEATHER_API_KEY")
    if not api_key:
        return {"error": "Weather API key not configured"}
    
    url = f"https://api.weatherapi.com/v1/forecast.json?key={api_key}&q={location}&days={days}"
    
    try:
        response = requests.get(url)
        response.raise_for_status()
        data = response.json()
        
        result = {
            "location": f"{data['location']['name']}, {data['location']['country']}",
            "current": {
                "temp_c": data['current']['temp_c'],
                "temp_f": data['current']['temp_f'],
                "condition": data['current']['condition']['text'],
                "humidity": data['current']['humidity']
            },
            "forecast": []
        }
        
        for day in data['forecast']['forecastday']:
            result['forecast'].append({
                "date": day['date'],
                "max_temp_c": day['day']['maxtemp_c'],
                "min_temp_c": day['day']['mintemp_c'],
                "condition": day['day']['condition']['text'],
                "chance_of_rain": day['day']['daily_chance_of_rain']
            })
        
        return result
    except Exception as e:
        return {"error": str(e)}
```

Parameters:
```json
{
  "location": {
    "type": "string",
    "description": "City name or zip code"
  },
  "days": {
    "type": "integer",
    "description": "Number of days for forecast",
    "minimum": 1,
    "maximum": 7,
    "default": 1
  }
}
```
