# Database Agent System Instructions

## Overview

The Database Agent is a specialized component of the AI Agent System responsible for managing the knowledge base and organizing information for efficient retrieval and learning. It serves as the system's long-term memory, storing and categorizing data that can be used to enhance the interpreter's capabilities over time.

This document provides detailed instructions on how to effectively use the Database Agent.

## Core Responsibilities

The Database Agent handles the following key responsibilities:

1. **Knowledge Storage**: Storing structured information in the database
2. **Data Organization**: Categorizing and tagging information for efficient retrieval
3. **Query Processing**: Responding to knowledge retrieval requests
4. **Knowledge Updates**: Maintaining and updating existing information
5. **Dataset Creation**: Generating QA datasets for training
6. **Superadmin Data Management**: Securely storing superadmin-specific information

## Interacting with the Database Agent

You can interact with the Database Agent through:

1. The Chat interface (by directing queries to the database)
2. The dedicated Database Management interface in the UI
3. Direct API calls to the database endpoints

## Knowledge Management Commands

### Adding Knowledge

To add information to the knowledge base:

```
Add to knowledge base: [information]
```

or

```
Remember this information: [information]
```

The Database Agent will:
1. Process the information
2. Extract key entities and concepts
3. Store it with appropriate metadata
4. Confirm successful storage

### Querying Knowledge

To retrieve information from the knowledge base:

```
What do you know about [topic]?
```

or

```
Retrieve information about [topic] from the knowledge base
```

The Database Agent will:
1. Search for relevant entries
2. Rank results by relevance
3. Return the most pertinent information
4. Provide source references

### Updating Knowledge

To update existing information:

```
Update knowledge base entry about [topic] with [new information]
```

The Database Agent will:
1. Locate the relevant entry
2. Merge or replace with new information
3. Update timestamps and metadata
4. Confirm the update

### Deleting Knowledge

To remove information:

```
Delete knowledge base entry about [topic]
```

The Database Agent will:
1. Request confirmation
2. Remove the entry if confirmed
3. Update related indices
4. Confirm deletion

## Advanced Features

### Knowledge Categories

The Database Agent organizes information into categories:

1. **Factual Knowledge**: Verified facts and information
2. **User Preferences**: Personal preferences and settings
3. **Task Information**: Details about ongoing or completed tasks
4. **Learning Insights**: Information derived from user interactions
5. **System Configuration**: System-specific settings and configurations

To specify a category when adding information:

```
Add to knowledge base in [category]: [information]
```

### Tagging System

You can add tags to knowledge entries for better organization:

```
Add to knowledge base with tags [tag1, tag2]: [information]
```

To search by tags:

```
Find knowledge entries with tag [tag]
```

### Knowledge Relationships

The Database Agent can establish relationships between knowledge entries:

```
Connect knowledge about [topic1] with [topic2]
```

To query related information:

```
What information is related to [topic]?
```

## Dataset Generation

The Database Agent can generate QA datasets for training:

```
Generate a dataset about [topic]
```

or

```
Create a QA dataset from recent conversations
```

The agent will:
1. Extract relevant question-answer pairs
2. Format them appropriately
3. Save them as a structured dataset
4. Provide access to the dataset

## Superadmin Data Management

For superadmin-specific data (restricted to authorized users):

```
Store as superadmin data: [information]
```

To retrieve superadmin data (requires authorization):

```
Retrieve superadmin data about [topic]
```

## Database Maintenance

### Backup Commands

To create a database backup:

```
Create a knowledge base backup
```

To restore from a backup:

```
Restore knowledge base from [backup_name]
```

### Optimization Commands

To optimize the database:

```
Optimize knowledge base
```

This will:
1. Reindex the database
2. Remove duplicates
3. Update vector embeddings
4. Improve retrieval performance

## Best Practices

1. **Be specific**: Provide clear, detailed information when adding to the knowledge base
2. **Use categories and tags**: Properly categorize and tag information for better organization
3. **Regular maintenance**: Periodically review and update knowledge entries
4. **Verify information**: Confirm the accuracy of information before adding it
5. **Use structured format**: When possible, provide information in a structured format

## Troubleshooting

If you encounter issues with the Database Agent:

1. **Retrieval problems**: Try using different keywords or more specific queries
2. **Storage failures**: Check for formatting issues or duplicate entries
3. **Performance issues**: Consider optimizing the database
4. **Access denied**: Verify you have the necessary permissions

## Examples

### Example 1: Adding Knowledge

User: "Add to knowledge base: The company's fiscal year ends on December 31st"

Agent: "Added to knowledge base: The company's fiscal year ends on December 31st. This information has been categorized under 'Factual Knowledge'."

### Example 2: Querying Knowledge

User: "What do you know about the company's fiscal year?"

Agent: "According to the knowledge base, the company's fiscal year ends on December 31st. This information was added on [date]."

### Example 3: Updating Knowledge

User: "Update knowledge base entry about fiscal year: The company's fiscal year now ends on March 31st"

Agent: "Updated knowledge base entry. Previous information: 'The company's fiscal year ends on December 31st' has been updated to 'The company's fiscal year now ends on March 31st'."

### Example 4: Creating a Dataset

User: "Generate a QA dataset about company policies"

Agent: "Generating QA dataset about company policies... Dataset created with 15 question-answer pairs. You can access it at [location]."
