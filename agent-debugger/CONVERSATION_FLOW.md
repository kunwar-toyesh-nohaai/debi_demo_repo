# 🎯 Using Debi AI Agent - Conversation Flow

## Initial Setup Flow

When you first connect to Debi AI, here's what happens:

### Step 1: Welcome Message

```
🤖 Debi: Hi, I'm Debi. I do full stack development.
         What would you like me to help you with?
```

### Step 2: Directory Path Request

```
🤖 Debi: First, could you please provide the absolute path
         to your project directory that you'd like me to work with?

💡 Placeholder shows: "Enter absolute path (e.g., C:\Users\YourName\Projects\MyApp)"
```

### Step 3: You Provide the Path

**Example (Windows):**

```
👤 You: C:\Users\kunwa\noha_repos\my-project
```

**Example (Linux/Mac):**

```
👤 You: /home/user/projects/my-project
```

### Step 4: Confirmation

**If path is valid:**

```
🤖 Debi: Great! I'll work with the project at: `C:\Users\kunwa\noha_repos\my-project`

         Now, what would you like me to help you with?
```

**If path is invalid:**

```
⚠️ Debi: I couldn't find a directory at: `C:\invalid\path`

         Please provide a valid absolute path to your project directory.
```

### Step 5: Normal Conversation

Once the directory is set, you can start describing your tasks:

```
👤 You: I have a bug in my login function where it throws an error
       when the email field is missing

🤖 Debi: [Analyzing your code...]
         [Provides diagnosis and fix]
```

## Important Notes

### ✅ Valid Directory Paths

The directory must:

- Be an **absolute path** (not relative)
- Actually exist on your system
- Be accessible by the backend server

**Windows Examples:**

```
C:\Users\YourName\Projects\MyApp
D:\Development\WebProjects\frontend
C:\code\my-python-project
```

**Linux/Mac Examples:**

```
/home/username/projects/myapp
/Users/username/Development/webapp
/var/www/my-site
```

### ❌ What Won't Work

- Relative paths: `./my-project` or `../code`
- Non-existent paths
- Paths without proper permissions
- Network paths that aren't mounted

### 🔄 Changing Directory

Currently, the directory is set per session. To change it:

1. Refresh the page
2. Reconnect
3. Provide a new directory path

## How It Works Behind the Scenes

```
┌─────────────────────────────────────────────────┐
│  1. Frontend connects to backend                │
│     ws://localhost:8000/ws/chat                 │
└────────────────┬────────────────────────────────┘
                 │
                 ▼
┌─────────────────────────────────────────────────┐
│  2. Backend sends welcome + directory request   │
└────────────────┬────────────────────────────────┘
                 │
                 ▼
┌─────────────────────────────────────────────────┐
│  3. User provides directory path                │
└────────────────┬────────────────────────────────┘
                 │
                 ▼
┌─────────────────────────────────────────────────┐
│  4. Backend validates path                      │
│     • os.path.isdir(path)                       │
│     • Stores in session state                   │
└────────────────┬────────────────────────────────┘
                 │
                 ▼
┌─────────────────────────────────────────────────┐
│  5. When processing messages:                   │
│     • os.chdir(working_directory)               │
│     • Run agent in that directory               │
│     • os.chdir(original_directory) after        │
└─────────────────────────────────────────────────┘
```

## Session State

Each WebSocket connection maintains:

```python
session_state = {
    'working_directory': '/path/to/project',
    'has_directory': True,
    'original_cwd': '/path/to/backend'
}
```

This ensures:

- ✅ Agent works in YOUR project directory
- ✅ Backend remains safe (always returns to original dir)
- ✅ Each session is isolated

## Example Full Session

```
🔌 Connected to Debi AI Agent

🤖 Debi: Hi, I'm Debi. I do full stack development.
         What would you like me to help you with?

🤖 Debi: First, could you please provide the absolute path
         to your project directory that you'd like me to work with?

👤 You:  C:\Users\kunwa\noha_repos\debi_demo_repo\test_dir

🤖 Debi: Great! I'll work with the project at: `C:\Users\kunwa\noha_repos\debi_demo_repo\test_dir`

         Now, what would you like me to help you with?

👤 You:  Can you check what files are in this project?

⏳       Processing your request...
⏳       Analyzing the issue. This may take a moment...

🤖 Debi: I've analyzed your project directory. Here's what I found:

         The project contains the following structure:
         - backend/
           - app/
           - requirements.txt
         - frontend/
           - noha/

         [... detailed analysis ...]
```

## Troubleshooting

### "I couldn't find a directory at..."

**Problem:** Path doesn't exist or is inaccessible

**Solutions:**

- Verify the path exists
- Use absolute path (not relative)
- Check for typos
- Ensure no trailing slashes (on Windows)
- Check folder permissions

### Agent is looking at wrong files

**Problem:** Directory not set correctly

**Solutions:**

- Refresh and reconnect
- Provide the correct absolute path
- Check backend logs for "Working directory set to: ..."

### Permission Denied

**Problem:** Backend can't access the directory

**Solutions:**

- Run backend with appropriate permissions
- Check folder permissions
- Avoid system directories

---

**Need more help?** Check the [full README](README.md) or [Architecture docs](ARCHITECTURE.md)
