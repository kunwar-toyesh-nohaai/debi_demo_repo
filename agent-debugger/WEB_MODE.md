# Web vs Terminal Mode - Technical Documentation

## Problem

The original agent was designed for terminal/CLI use and includes interactive confirmation prompts that use `input()` to get user confirmation before:

- Writing files
- Making git commits

When running through the WebSocket API, these `input()` calls **block execution** and wait for terminal input, preventing responses from reaching the frontend.

## Solution

Created a **dual-mode architecture**:

### 1. Terminal Mode (CLI)

- **File**: `agent_loop.py`
- **Uses**: `confirmation_handler.py` with `input()` prompts
- **For**: Direct CLI usage via `main.py`
- **Behavior**: Asks for confirmation before changes

### 2. Web Mode (WebSocket/API)

- **File**: `agent_loop_web.py`
- **Skips**: All terminal confirmations
- **For**: WebSocket and REST API usage via `api_server.py`
- **Behavior**: Auto-applies changes with logging

## Architecture Comparison

```
┌─────────────────────────────────────────────────────────┐
│                    Terminal Mode                        │
├─────────────────────────────────────────────────────────┤
│                                                         │
│  main.py                                                │
│    ↓                                                    │
│  agent_loop.py                                          │
│    ↓                                                    │
│  confirmation_handler.py                                │
│    ↓                                                    │
│  input() ← BLOCKS waiting for user                     │
│                                                         │
└─────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────┐
│                      Web Mode                           │
├─────────────────────────────────────────────────────────┤
│                                                         │
│  api_server.py                                          │
│    ↓                                                    │
│  agent_loop_web.py                                      │
│    ↓                                                    │
│  Auto-approve all changes                               │
│    ↓                                                    │
│  Return response immediately ← NO BLOCKING              │
│                                                         │
└─────────────────────────────────────────────────────────┘
```

## Key Differences

### agent_loop.py (Terminal)

```python
def write_file_wrapper(input_str: str):
    # Parse input
    confirmed, error = confirm_file_write(filepath, content, issue)
    # ↑ BLOCKS HERE waiting for input()

    if confirmed:
        return write_file(filepath, content)
    else:
        raise RestartFlowException()
```

### agent_loop_web.py (Web)

```python
def write_file_wrapper_web(input_str: str):
    # Parse input
    # NO CONFIRMATION - just log and proceed
    logger.info(f"Writing to file: {filepath}")

    result = write_file(filepath, content)
    _record_file_change(filepath)
    return result
```

## Functions Comparison

| Function      | Terminal Mode              | Web Mode                       |
| ------------- | -------------------------- | ------------------------------ |
| Create agent  | `create_agent()`           | `create_agent_web()`           |
| Run agent     | `run_agent()`              | `run_agent_web()`              |
| Write file    | `write_file_wrapper()`     | `write_file_wrapper_web()`     |
| Git commit    | `commit_changes_wrapper()` | `commit_changes_wrapper_web()` |
| Confirmations | ✅ Required                | ❌ Skipped                     |

## Web Mode Features

### Added Instructions

The web agent includes special instructions:

```python
IMPORTANT WEB MODE INSTRUCTIONS:
- You are running in web mode through a chat interface
- File changes will be applied automatically WITHOUT confirmation
- Git commits will be made automatically WITHOUT confirmation
- Always explain what you're doing before making changes
- Provide clear summaries of changes made
- Be concise but thorough in your responses
```

### Auto-Approval with Logging

Instead of asking for confirmation:

```python
# Terminal: Asks "Should I apply these changes?"
# Web: Logs and proceeds

logger.info(f"Writing to file: {filepath}")
logger.info(f"Content length: {len(final_content)} characters")
result = write_file(filepath, final_content)
```

### Error Handling

Both modes have similar error handling, but web mode returns errors as strings instead of raising exceptions:

```python
# Terminal: May raise RestartFlowException
# Web: Returns error message to frontend

try:
    result = write_file(filepath, content)
except Exception as e:
    return f"Error writing file: {str(e)}"
```

## API Server Updates

### Imports Changed

```python
# Before
from agent_loop import create_agent, run_agent, reset_applied_file_changes

# After
from agent_loop_web import create_agent_web, run_agent_web, reset_applied_file_changes
```

### Usage Updated

```python
# In ConnectionManager
def get_or_create_agent(self):
    if self.agent_instance is None:
        self.agent_instance = create_agent_web(api_key)  # ← Web version
    return self.agent_instance

# In WebSocket handler
response = await loop.run_in_executor(
    None,
    run_agent_web,  # ← Web version
    agent,
    user_message
)
```

## Safety Considerations

### Terminal Mode

- ✅ User reviews all changes before applying
- ✅ Can decline and restart
- ✅ Full control over what happens

### Web Mode

- ⚠️ Auto-applies changes (no confirmation)
- ✅ All changes are logged
- ✅ Working directory is isolated per session
- ✅ Backend always returns to original directory
- ℹ️ **User should trust the agent's decisions**

## Future Enhancements

Potential improvements for web mode:

### 1. WebSocket Confirmations

Instead of auto-approving, send confirmation requests to frontend:

```python
# Backend
await send_message({
    "type": "confirmation_request",
    "action": "write_file",
    "filepath": "app.py",
    "diff": "...",
    "request_id": "abc123"
})

# Wait for response
# Frontend sends back:
{
    "type": "confirmation_response",
    "request_id": "abc123",
    "approved": true
}
```

### 2. Configurable Auto-Approval

Allow users to choose:

```python
session_state = {
    'auto_approve': True,  # ← User preference
    'working_directory': '/path/to/project'
}
```

### 3. Undo Functionality

Track changes and allow rollback:

```python
{
    "type": "undo",
    "change_id": "xyz789"
}
```

## Testing Both Modes

### Terminal Mode

```bash
cd agent-debugger/backend
python main.py
# Will prompt for confirmations in terminal
```

### Web Mode

```bash
# Terminal 1
cd agent-debugger/backend
python api_server.py

# Terminal 2
cd agent-debugger/frontend/noha
npm run dev

# Open browser at http://localhost:5173
# No terminal prompts - all responses go to frontend
```

## Logging

Both modes log extensively:

```
INFO - Writing to file: app.py
INFO - Content length: 1234 characters
INFO - Successfully wrote file: app.py
```

Check logs:

- **Terminal mode**: `agent_debugger_YYYYMMDD_HHMMSS.log`
- **Web mode**: Same file format, both modes share logging

## Summary

- ✅ **Terminal mode** retained for CLI use with confirmations
- ✅ **Web mode** created for WebSocket/API with auto-approval
- ✅ No blocking `input()` calls in web mode
- ✅ Frontend now receives all responses
- ✅ Both modes share the same tools (file/git operations)
- ✅ Both modes use the same LLM and prompts
- ✅ Only difference: confirmation handling

**Result**: Agent responses now flow smoothly to the frontend! 🎉
