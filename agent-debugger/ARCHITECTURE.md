# Debi AI Agent - Architecture Overview

## System Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                        User's Browser                            │
│                   http://localhost:5173                          │
└────────────────────────────┬────────────────────────────────────┘
                             │
                             │ WebSocket Connection
                             │ (Real-time bidirectional)
                             │
┌────────────────────────────▼────────────────────────────────────┐
│                     Frontend (React + TypeScript)                │
│  ┌────────────────────────────────────────────────────────────┐ │
│  │  Modern Chat Interface                                     │ │
│  │  • Real-time messaging                                     │ │
│  │  • Auto-scroll & animations                                │ │
│  │  • Connection status monitoring                            │ │
│  │  • Glassmorphism design                                    │ │
│  └────────────────────────────────────────────────────────────┘ │
│                                                                   │
│  Tech Stack:                                                      │
│  • React 18 with TypeScript                                      │
│  • Vite (build tool)                                             │
│  • WebSocket API                                                 │
│  • CSS3 (modern features)                                        │
└───────────────────────────────────────────────────────────────────┘

                             │
                             │ ws://localhost:8000/ws/chat
                             │
┌────────────────────────────▼────────────────────────────────────┐
│                 Backend API (FastAPI)                            │
│               http://localhost:8000                              │
│  ┌────────────────────────────────────────────────────────────┐ │
│  │  WebSocket Handler                                         │ │
│  │  • Manages connections                                     │ │
│  │  • Routes messages to agent                                │ │
│  │  • Sends real-time updates                                 │ │
│  └────────────────────────┬───────────────────────────────────┘ │
│                           │                                       │
│  ┌────────────────────────▼───────────────────────────────────┐ │
│  │  LangChain Agent                                           │ │
│  │  • Processes user requests                                 │ │
│  │  • Orchestrates tools                                      │ │
│  │  • Manages conversation flow                               │ │
│  └────────────────────────┬───────────────────────────────────┘ │
│                           │                                       │
│  Tech Stack:               │                                      │
│  • FastAPI                 │                                      │
│  • LangChain              │                                      │
│  • Google Gemini AI       │                                      │
│  • WebSockets             │                                      │
└───────────────────────────┼───────────────────────────────────────┘
                            │
          ┌─────────────────┼─────────────────┐
          │                 │                 │
┌─────────▼────────┐ ┌──────▼──────┐ ┌──────▼──────────┐
│  File Tools      │ │  Git Tools  │ │  Google Gemini  │
│                  │ │             │ │    AI API       │
│  • list_files    │ │  • commit   │ │                 │
│  • read_file     │ │  • status   │ │  • Analysis     │
│  • write_file    │ │  • log      │ │  • Code Gen     │
└──────────────────┘ └─────────────┘ └─────────────────┘
```

## Data Flow

### 1. User Sends Message

```
User Types → Frontend validates → WebSocket sends JSON:
{
  "type": "message",
  "content": "Fix the login bug",
  "repo_url": "optional"
}
```

### 2. Backend Processing

```
FastAPI receives → Creates/Gets Agent → Runs LangChain Agent
                                              ↓
                                    Agent uses tools:
                                    • Lists project files
                                    • Reads relevant code
                                    • Analyzes with Gemini AI
                                    • Suggests fixes
```

### 3. Response Streaming

```
Backend sends status updates:
• "Processing your request..."
• "Analyzing the issue..."
• Final response with suggestions
```

### 4. User Confirmation (if needed)

```
Agent suggests changes → User approves → Agent applies → Git commit
```

## Key Features

### Frontend

- 🎨 **Modern UI**: Glassmorphism, gradients, smooth animations
- 🔄 **Real-time**: WebSocket for instant communication
- 📱 **Responsive**: Works on all screen sizes
- ♿ **Accessible**: Keyboard navigation, screen reader support
- 🎯 **User-friendly**: Example prompts, auto-scroll, status indicators

### Backend

- ⚡ **Fast**: Async FastAPI with WebSocket support
- 🤖 **Intelligent**: LangChain + Google Gemini AI
- 🛡️ **Safe**: Confirmation before file changes
- 📝 **Logged**: Comprehensive logging for debugging
- 🔌 **RESTful**: Also provides standard REST endpoints

### Agent Capabilities

- 🔍 **Code Analysis**: Understands project structure
- 🐛 **Bug Detection**: Identifies issues in code
- 💡 **Smart Suggestions**: Provides actionable fixes
- ✍️ **Code Generation**: Can write or modify code
- 📚 **Context Aware**: Maintains conversation context

## Technology Stack

| Layer        | Technology             | Purpose                     |
| ------------ | ---------------------- | --------------------------- |
| Frontend     | React 18 + TypeScript  | UI framework                |
| Build Tool   | Vite                   | Fast development & bundling |
| Styling      | CSS3                   | Modern, custom styling      |
| Backend      | FastAPI                | Web framework               |
| Server       | Uvicorn                | ASGI server                 |
| AI Framework | LangChain              | Agent orchestration         |
| AI Model     | Google Gemini          | Language understanding      |
| Protocol     | WebSocket              | Real-time communication     |
| State        | In-memory + Filesystem | Conversation & file storage |

## Security Considerations

1. **API Key Protection**: Stored in `.env` file (gitignored)
2. **CORS**: Configured for localhost (customize for production)
3. **File Access**: Agent only accesses current working directory
4. **User Confirmation**: Required before any file modifications
5. **Git Safety**: Only commits locally, never pushes automatically

## Scalability Notes

### Current Architecture

- **Single User**: Designed for local development
- **Session State**: In-memory (resets on server restart)
- **File Operations**: Direct filesystem access

### Production Considerations

- Add authentication & authorization
- Implement session persistence (Redis/DB)
- Add rate limiting
- Deploy backend & frontend separately
- Use environment-specific configurations
- Add monitoring & error tracking

## Development Workflow

```
┌──────────────┐    ┌──────────────┐    ┌──────────────┐
│   Make       │    │   Test in    │    │   Deploy     │
│   Changes    │ →  │   Browser    │ →  │   Changes    │
└──────────────┘    └──────────────┘    └──────────────┘
      ↓                    ↓                    ↓
   Hot Reload         Live Reload         Git Commit
   (Vite/Uvicorn)    (Auto Refresh)      (Version Control)
```

## File Structure

```
agent-debugger/
├── backend/                 # Python backend
│   ├── api_server.py       # FastAPI application ⭐
│   ├── agent_loop.py       # LangChain agent
│   ├── main.py             # CLI interface
│   ├── prompts.py          # AI prompts
│   ├── confirmation_handler.py
│   ├── logging_config.py
│   ├── requirements.txt    # Python deps
│   └── tools/
│       ├── file_tools.py   # File operations
│       └── git_tools.py    # Git operations
│
├── frontend/               # React frontend
│   └── noha/
│       ├── src/
│       │   ├── App.tsx     # Main component ⭐
│       │   ├── App.css     # Chat styling
│       │   └── index.css   # Global styles
│       ├── index.html
│       └── package.json    # Node deps
│
├── .env                    # Environment variables
├── .env.example            # Template
├── .gitignore
├── README.md               # Full documentation
├── QUICKSTART.md           # Quick start guide
├── ARCHITECTURE.md         # This file
├── setup-backend.bat       # Backend setup
├── setup-frontend.bat      # Frontend setup
├── start-backend.bat       # Start backend
└── start-frontend.bat      # Start frontend
```

## API Endpoints

### WebSocket

- **`/ws/chat`**: Real-time chat interface
  - Input: JSON with message content
  - Output: Streaming responses

### REST

- **`GET /`**: API info
- **`GET /health`**: Health check
- **`POST /debug`**: Synchronous debugging (alternative to WebSocket)

## Environment Variables

| Variable       | Required | Description           |
| -------------- | -------- | --------------------- |
| GOOGLE_API_KEY | Yes      | Google Gemini API key |

## Performance Optimization

1. **Frontend**

   - Lazy load components
   - Virtual scrolling for long chats
   - Debounce user input
   - Memoize expensive computations

2. **Backend**

   - Async operations
   - Connection pooling
   - Response streaming
   - Caching for repeated queries

3. **AI Calls**
   - Batch requests when possible
   - Cache common responses
   - Optimize prompts for token usage
   - Set appropriate timeouts

---

_Architecture designed for local development and easy deployment_ 🚀
