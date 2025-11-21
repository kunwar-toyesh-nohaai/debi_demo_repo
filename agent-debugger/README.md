# Debi AI Agent - Full Stack Debugging Assistant

A modern, full-stack AI-powered debugging assistant with a beautiful chat interface. Debi can analyze your codebase, debug issues, suggest fixes, and apply changes with your approval.

## 🌟 Features

- **💬 Real-time Chat Interface**: Beautiful, modern UI with WebSocket-based real-time communication
- **🤖 AI-Powered Analysis**: Uses Google's Gemini AI to understand and debug code
- **🔍 Intelligent Code Inspection**: Automatically analyzes relevant files in your codebase
- **🐛 Bug Fixing**: Suggests and applies fixes with your confirmation
- **✅ Git Integration**: Automatically commits fixes with appropriate commit messages
- **📱 Responsive Design**: Works beautifully on desktop and mobile devices

## 📁 Project Structure

```
agent-debugger/
├── backend/                 # Python FastAPI backend
│   ├── api_server.py       # FastAPI server with WebSocket support
│   ├── agent_loop.py       # LangChain agent implementation
│   ├── main.py             # Original CLI interface
│   ├── prompts.py          # AI prompts
│   ├── tools/              # Agent tools (file & git operations)
│   └── requirements.txt    # Python dependencies
│
└── frontend/               # React + TypeScript frontend
    └── noha/
        ├── src/
        │   ├── App.tsx     # Main chat interface
        │   ├── App.css     # Chat styling
        │   └── index.css   # Global styles
        └── package.json    # Node dependencies
```

## 🚀 Getting Started

### Prerequisites

- **Python 3.8+**
- **Node.js 18+** and **npm**
- **Google API Key** (Get one from [Google AI Studio](https://makersuite.google.com/app/apikey))

### Backend Setup

1. **Navigate to the backend directory**:

   ```bash
   cd agent-debugger/backend
   ```

2. **Install Python dependencies**:

   ```bash
   pip install -r requirements.txt
   ```

3. **Set up environment variables**:

   Create a `.env` file in the `agent-debugger` directory (parent of backend):

   ```bash
   GOOGLE_API_KEY=your-api-key-here
   ```

4. **Start the backend server**:

   ```bash
   python api_server.py
   ```

   The server will start on `http://localhost:8000`

### Frontend Setup

1. **Navigate to the frontend directory**:

   ```bash
   cd agent-debugger/frontend/noha
   ```

2. **Install Node dependencies**:

   ```bash
   npm install
   ```

3. **Start the development server**:

   ```bash
   npm run dev
   ```

   The frontend will start on `http://localhost:5173`

## 💻 Usage

### Using the Chat Interface

1. **Open your browser** and navigate to `http://localhost:5173`

2. **Start chatting** with Debi! You can:

   - Describe bugs you're encountering
   - Ask for code reviews
   - Request new features to be implemented
   - Get help with debugging

3. **Example prompts**:
   - "I have a bug where my login function throws a KeyError when the user doesn't provide an email field"
   - "Add user authentication to my Flask application"
   - "Review my API endpoint code and suggest improvements"

### Using the CLI (Original Interface)

If you prefer the terminal interface:

```bash
cd agent-debugger/backend
python main.py
```

## 🎨 Design Features

The frontend features a **premium, modern design** with:

- **Dark theme** with glassmorphism effects
- **Vibrant gradients** (purple & pink accent colors)
- **Smooth animations** and transitions
- **Real-time status indicators**
- **Auto-scrolling chat**
- **Responsive layout** for all screen sizes
- **Example prompts** to get started quickly

## 🔌 API Endpoints

### WebSocket

- **`/ws/chat`**: Real-time chat with the AI agent
  - Supports bidirectional communication
  - Automatic reconnection on disconnect

### REST API

- **`GET /`**: API information
- **`GET /health`**: Health check endpoint
- **`POST /debug`**: Synchronous debugging endpoint
  ```json
  {
    "bug_description": "Describe your bug here",
    "repo_url": "optional repo url"
  }
  ```

## 🛡️ Safety Features

- **Confirmation Required**: Never applies changes without explicit approval
- **Git Integration**: All changes are committed locally (not pushed)
- **Safe Path Handling**: Validates all file operations
- **Error Recovery**: Graceful handling of failures
- **Comprehensive Logging**: Full audit trail of all operations

## 🔧 Development

### Backend Development

The backend uses:

- **FastAPI** for the web framework
- **WebSockets** for real-time communication
- **LangChain** for AI agent orchestration
- **Google Gemini** for AI capabilities

### Frontend Development

The frontend uses:

- **React 18** with TypeScript
- **Vite** for fast development
- **WebSocket API** for real-time updates
- **CSS3** with modern features (gradients, animations, glassmorphism)

## 📝 Environment Variables

Create a `.env` file in the `agent-debugger` directory:

```bash
GOOGLE_API_KEY=your-google-api-key
```

## 🐛 Troubleshooting

### Backend Issues

- **"GOOGLE_API_KEY not set"**: Ensure `.env` file exists in `agent-debugger/` directory
- **Port 8000 already in use**: Change the port in `api_server.py`
- **Module import errors**: Run `pip install -r requirements.txt`

### Frontend Issues

- **WebSocket connection failed**: Ensure backend is running on port 8000
- **Dependencies error**: Run `npm install` again
- **Port 5173 in use**: Vite will automatically use another port

### Connection Issues

- **Frontend can't connect**: Check that both servers are running
- **CORS errors**: Backend is configured to allow all origins in development

## 📄 License

This project is provided as-is for educational and development purposes.

## 🙏 Acknowledgments

- Built with [Google Gemini AI](https://ai.google.dev/)
- Powered by [LangChain](https://langchain.com/)
- UI framework: [React](https://react.dev/)
- Backend: [FastAPI](https://fastapi.tiangolo.com/)
