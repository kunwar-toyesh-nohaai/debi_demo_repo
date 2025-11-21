# 🚀 Quick Start Guide

Get Debi AI Agent up and running in under 5 minutes!

## Prerequisites

- ✅ Python 3.8 or higher
- ✅ Node.js 18 or higher
- ✅ Google API Key ([Get one here](https://makersuite.google.com/app/apikey))

## Step-by-Step Setup

### 1️⃣ Configure Your API Key

1. Copy the example environment file:

   ```bash
   copy .env.example .env
   ```

2. Open `.env` and replace `your-api-key-here` with your actual Google API key:
   ```
   GOOGLE_API_KEY=AIzaSy...your-actual-key-here
   ```

### 2️⃣ Set Up Backend

**Option A: Using the setup script (Recommended)**

```bash
setup-backend.bat
```

**Option B: Manual setup**

```bash
cd backend
pip install -r requirements.txt
cd ..
```

### 3️⃣ Set Up Frontend

**Option A: Using the setup script (Recommended)**

```bash
setup-frontend.bat
```

**Option B: Manual setup**

```bash
cd frontend/noha
npm install
cd ../..
```

### 4️⃣ Start the Application

**You'll need TWO terminal windows:**

**Terminal 1 - Backend:**

```bash
start-backend.bat
```

Wait for: `Application startup complete`

**Terminal 2 - Frontend:**

```bash
start-frontend.bat
```

Wait for: `Local: http://localhost:5173`

### 5️⃣ Open Your Browser

Navigate to: **http://localhost:5173**

🎉 **You're ready to chat with Debi!**

## First Steps

Try these example prompts:

1. **Debug a bug:**

   ```
   I have a bug where my login function throws a KeyError
   when the user doesn't provide an email field
   ```

2. **Add a feature:**

   ```
   Add user authentication to my Flask application
   ```

3. **Code review:**
   ```
   Review my API endpoint code and suggest improvements
   for security and performance
   ```

## Troubleshooting

### Backend won't start

- ❌ **"GOOGLE_API_KEY not set"** → Check your `.env` file
- ❌ **"Module not found"** → Run `pip install -r backend/requirements.txt`
- ❌ **Port 8000 in use** → Change port in `backend/api_server.py`

### Frontend won't start

- ❌ **"Cannot find module"** → Run `npm install` in `frontend/noha`
- ❌ **Port 5173 in use** → Vite will auto-select another port

### Can't connect to backend

- ❌ Make sure backend is running on port 8000
- ❌ Check console for WebSocket errors
- ❌ Backend URL in `App.tsx` should be `ws://localhost:8000/ws/chat`

## Usage Tips

### Chat Interface Features

- **📝 Multi-line input**: Press `Shift + Enter` for new lines
- **🚀 Send message**: Press `Enter` to send
- **🤖 Auto-scroll**: Messages auto-scroll to the latest
- **🔄 Auto-reconnect**: Frontend reconnects automatically if disconnected
- **💡 Example prompts**: Click any example card to use it

### Best Practices

1. **Be specific** with your bug descriptions
2. **Include error messages** when debugging
3. **Mention file names** if you know them
4. **Review changes** before accepting them

## Next Steps

- 📖 Read the full [README.md](README.md) for advanced features
- 🛠️ Check `backend/tools/` to understand available operations
- 🎨 Customize the UI in `frontend/noha/src/App.css`
- 🔧 Modify prompts in `backend/prompts.py`

## Need Help?

- Backend logs: Check console where `start-backend.bat` is running
- Frontend logs: Press `F12` in browser → Console tab
- Agent logs: Look for `agent_debugger_*.log` files in `backend/`

---

**Happy coding with Debi! 🤖✨**
