# DOCGET - AI-Powered Terminal Chat CLI

A terminal-based chatbot CLI powered by Claude AI with TOON (Task-Objective-Output-Notes) architecture.

## Architecture

### TOON Structure
The system uses TOON architecture to structure requests:
- **Task**: What needs to be done
- **Objective**: Why it needs to be done / expected outcome
- **Output**: Expected output format
- **Notes**: Additional context or constraints

### Pluggable Agent System
The architecture supports pluggable agents:
- `BaseAgent`: Abstract interface for all agents
- `ClaudeAgent`: Claude AI implementation (current)
- `AnalyzerAgent`: Analyzes user requests and creates TOON structures

Future agents can be added by implementing the `BaseAgent` interface.

## Setup

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Set up your Anthropic API key:
```bash
export ANTHROPIC_API_KEY='your-api-key-here'
```

Or create a `.env` file (see `.env.example`).

## Usage

Run the chatbot:
```bash
./docget
```

### Available Commands

- `/help` - Show help message
- `/clear` - Clear conversation history
- `/history` - Show conversation history
- `/debug` - Toggle debug mode (shows TOON structures and metadata)
- `/exit` - Exit the chat

### Debug Mode

Enable debug mode to see how your requests are structured:
```
You: /debug
Debug mode enabled.

You: What is Python?

[DEBUG] TOON Request:
  Task: What is Python?
  Objective: Understand and respond to user request
  Output Format: conversational text
  Notes: User query from CLI

[DEBUG] Response metadata:
  Model: claude-3-5-sonnet-20241022
  Tokens: {'input_tokens': 15, 'output_tokens': 120}