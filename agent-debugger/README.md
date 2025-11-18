# AI Code Debugging Agent

An intelligent debugging agent built with LangChain and Google's Gemini that can analyze bug descriptions, identify problematic files, suggest fixes, and apply them with your confirmation.

## Features

- 🔍 **Automatic Bug Analysis**: Analyzes bug descriptions and identifies relevant files
- 📁 **File Inspection**: Lists and reads project files to understand the codebase
- 🐛 **Bug Identification**: Reasons about the issue and explains it clearly
- 🔧 **Fix Suggestions**: Proposes exact code modifications to fix the bug
- ✅ **Confirmation Required**: Always asks for approval before applying changes
- 📝 **Git Integration**: Automatically commits fixes with appropriate commit messages
- 📋 **Comprehensive Logging**: All agent activity, tool usage, and outputs are logged to timestamped log files

## Installation

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Set Up Google API Key

You need a Google API key to use the Gemini model. Get one from [Google AI Studio](https://makersuite.google.com/app/apikey).

#### Option 1: Using a .env file (Recommended)

Create a `.env` file in the `agent-debugger` directory (same level as `main.py`) with the following content:

```bash
GOOGLE_API_KEY=your-api-key-here
```

**Location**: `agent-debugger/.env`

The `.env` file will be automatically loaded when you run the application. **Important**: Make sure to add `.env` to your `.gitignore` file to avoid committing your API key!

#### Option 2: Using Environment Variables

##### On Linux/macOS:
```bash
export GOOGLE_API_KEY='your-api-key-here'
```

##### On Windows (Command Prompt):
```cmd
set GOOGLE_API_KEY=your-api-key-here
```

##### On Windows (PowerShell):
```powershell
$env:GOOGLE_API_KEY='your-api-key-here'
```

#### Permanent Setup (Optional)

To make the API key persistent, add it to your shell configuration file:
- **Linux/macOS**: Add to `~/.bashrc` or `~/.zshrc`
- **Windows**: Add as a system environment variable through System Properties

## Usage

### Basic Usage

1. Navigate to your project directory (the one containing the bug):
   ```bash
   cd /path/to/your/project
   ```

2. Run the agent:
   ```bash
   python main.py
   ```

3. Enter your bug description when prompted. Press Enter twice (or Ctrl+Z then Enter on Windows) when finished.

4. The agent will:
   - List project files
   - Identify relevant files
   - Read and analyze the code
   - Explain the bug
   - Suggest a fix
   - Ask for confirmation

5. Type `yes` to apply the fix, or `no` to decline.

6. If approved, the agent will:
   - Apply the fix to the file
   - Commit the changes with an appropriate commit message

### Example Session

```
============================================================
AI Code Debugging Agent
============================================================

Please describe the bug you'd like me to debug:
(Press Enter twice or Ctrl+Z then Enter on Windows to finish)

The login function is throwing a KeyError when the user
doesn't provide an email field. It should handle missing
fields gracefully.

Initializing agent...

Agent is analyzing the bug. This may take a moment...

[Agent analyzes files, reads code, suggests fix]

Should I apply this change? (yes/no)
yes

[Agent applies fix and commits]
```

## Project Structure

```
agent-debugger/
├── main.py              # CLI entry point
├── agent_loop.py        # LangChain agent implementation
├── prompts.py           # System and user prompts
├── requirements.txt     # Python dependencies
├── tools/
│   ├── __init__.py
│   ├── file_tools.py   # File operations (list, read, write)
│   └── git_tools.py    # Git operations (commands, commits)
└── README.md           # This file
```

## Safety Features

### File Operations
- **Safe Path Handling**: Validates paths before operations
- **Error Handling**: All tools return explicit error messages
- **Permission Checks**: Handles permission errors gracefully
- **Encoding Safety**: Handles UTF-8 encoding with fallback error messages

### Git Operations
- **Repository Validation**: Checks if directory is a git repository
- **Timeout Protection**: Commands timeout after 30 seconds
- **Error Reporting**: Returns detailed error messages on failure

### Agent Behavior
- **Confirmation Required**: Never applies changes without explicit user approval
- **Verbose Output**: Shows all agent reasoning steps
- **Error Recovery**: Handles parsing errors and tool failures gracefully

## Logging

All agent activity is automatically logged to timestamped log files in the `agent-debugger` directory. Log files are named with the format: `agent_debugger_YYYYMMDD_HHMMSS.log`

The logging system captures:
- Application startup and initialization
- Bug descriptions received
- Agent creation and configuration
- All tool invocations (file operations, git commands)
- Agent reasoning steps and actions
- Final agent responses
- Errors and exceptions

Log files include:
- **INFO level**: Important events and status updates
- **DEBUG level**: Detailed execution steps, tool inputs/outputs, and agent reasoning

You can find your log files in the same directory as `main.py`. Log files are automatically created for each run, so you can review the complete execution history.

## Important Notes

### File Writes
- The agent will **overwrite** existing files when applying fixes
- Always ensure you have:
  - Backed up your code (git commit before running)
  - Reviewed the suggested fix carefully
  - Confirmed you want to apply the change

### Git Commits
- The agent commits to your **local** repository only
- It does **not** push to remote repositories
- Commit messages are auto-generated based on the fix
- All changes are staged automatically before committing

### Working Directory
- The agent operates in the current working directory
- Make sure you're in the correct project directory before running
- File paths should be relative to the current directory

## Troubleshooting

### "GOOGLE_API_KEY environment variable is not set"
- Make sure you've exported the API key as shown in the Installation section
- Verify the key is set: `echo $GOOGLE_API_KEY` (Linux/macOS) or `echo %GOOGLE_API_KEY%` (Windows)

### "Git is not installed or not found in PATH"
- Install Git: https://git-scm.com/downloads
- Ensure Git is in your system PATH

### "Error: 'path' is not a git repository"
- Make sure you're running the agent from within a git repository
- Initialize git if needed: `git init`

### Agent takes too long
- Large codebases may take time to analyze
- The agent reads multiple files and reasons about the code
- Be patient, or try with a more specific bug description

## Limitations

- Works best with text-based source code files
- Binary files may cause encoding errors
- Very large files (>1MB) may be slow to process
- Requires internet connection for API calls
- API usage may incur costs depending on your Google Cloud plan

## License

This project is provided as-is for educational and development purposes.

