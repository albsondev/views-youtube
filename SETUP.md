# YouTube Automation Agent - Setup Guide

## 🚀 Quick Start

### Prerequisites
- Python 3.9 or higher
- Node.js 18 or higher
- Git

### 1. Clone or Navigate to Project
```bash
cd c:\Users\ddalb\OneDrive\Documents\PROJETOS\views-youtube
```

### 2. Backend Setup

```bash
# Navigate to backend
cd backend

# Create virtual environment
python -m venv venv

# Activate virtual environment
venv\Scripts\activate  # Windows

# Install dependencies
pip install -r requirements.txt

# Install Playwright browsers
playwright install chromium

# Create .env file
copy ..\.env.example .env
```

Edit `.env` file and configure:
- `TARGET_CHANNEL_URL`: URL of the YouTube channel to automate
- `GOOGLE_EMAIL` and `GOOGLE_PASSWORD`: Your Google account credentials
- Other settings as needed

### 3. Frontend Setup

```bash
# Navigate to frontend (from project root)
cd frontend

# Install dependencies
npm install
```

### 4. Running the Application

**Terminal 1 - Backend:**
```bash
cd backend
venv\Scripts\activate
python main.py
```
Backend will run on `http://localhost:8000`

**Terminal 2 - Frontend:**
```bash
cd frontend
npm run dev
```
Frontend will run on `http://localhost:5173`

### 5. Using the Application

1. Open browser and go to `http://localhost:5173`
2. Click "Login to Google" and enter your credentials
3. Configure the channel URL and settings
4. Click "Start Automation"
5. Monitor activity in real-time

## ⚙️ Configuration Options

### Backend (.env)

| Variable | Description | Default |
|----------|-------------|---------|
| `TARGET_CHANNEL_URL` | YouTube channel to automate | Required |
| `HEADLESS_MODE` | Run browser in headless mode | `false` |
| `MIN_WATCH_TIME` | Minimum video watch time (seconds) | `30` |
| `MAX_WATCH_TIME` | Maximum video watch time (seconds) | `180` |
| `ACTION_DELAY_MIN` | Minimum delay between actions (seconds) | `2` |
| `ACTION_DELAY_MAX` | Maximum delay between actions (seconds) | `5` |
| `USE_AI_COMMENTS` | Use OpenAI for comment generation | `false` |
| `OPENAI_API_KEY` | OpenAI API key (if using AI comments) | Optional |

## 📚 API Documentation

Once the backend is running, visit `http://localhost:8000/docs` for interactive API documentation.

## 🔧 Troubleshooting

### Playwright Installation Issues
```bash
# Reinstall Playwright
pip uninstall playwright
pip install playwright
playwright install chromium
```

### Port Already in Use
Change ports in:
- Backend: `.env` file (`API_PORT`)
- Frontend: `vite.config.js` (add server.port option)

### Login Fails
- Google may require 2FA - use app-specific password
- Check if account has unusual activity protection
- Try running in non-headless mode (`HEADLESS_MODE=false`)

## ⚠️ Important Notes

1. **Educational Purpose Only**: This violates YouTube ToS
2. **Account Risk**: Your Google account may be banned
3. **Rate Limiting**: Built-in delays help avoid detection
4. **Session Persistence**: Login session is saved locally

## 🎯 Features

- ✅ Automated Google login
- ✅ Channel subscription
- ✅ Realistic video watching patterns
- ✅ Smart comment generation
- ✅ Like automation
- ✅ Real-time dashboard
- ✅ Activity logging
- ✅ Session persistence

## 📝 Development

### Backend Structure
```
backend/
├── agent/              # Automation modules
│   ├── browser_controller.py
│   ├── account_manager.py
│   ├── youtube_navigator.py
│   ├── video_watcher.py
│   ├── comment_generator.py
│   ├── interaction_handler.py
│   └── youtube_agent.py
├── config/             # Configuration
│   └── settings.py
├── utils/              # Utilities
│   └── logger.py
└── main.py             # FastAPI server
```

### Frontend Structure
```
frontend/
└── src/
    ├── components/     # React components
    │   ├── Dashboard.jsx
    │   └── Dashboard.css
    ├── services/       # API client
    │   └── api.js
    ├── App.jsx
    └── App.css
```

## 🔐 Security

- Never commit `.env` file
- Use app-specific passwords for Google
- Keep session files private
- Don't share API keys

## 📄 License

MIT - Educational purposes only
