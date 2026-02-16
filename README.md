# YouTube Automation Agent 🤖

Educational project demonstrating web automation, browser control, and full-stack development.

## ⚠️ Disclaimer

This project is for **educational purposes only**. Automated interactions with YouTube violate their Terms of Service and may result in account suspension. Use responsibly in controlled environments.

## 🏗️ Architecture

- **Backend**: Python + FastAPI + Playwright
- **Frontend**: React + Vite
- **Purpose**: Learn web automation, anti-detection techniques, and full-stack integration

## 🚀 Quick Start

### Backend Setup

```bash
cd backend
python -m venv venv
venv\Scripts\activate  # Windows
pip install -r requirements.txt
playwright install chromium
python main.py
```

Backend runs on `http://localhost:8002`

### Frontend Setup

```bash
cd frontend
npm install
npm run dev
```

Frontend runs on `http://localhost:5173`

## 📁 Project Structure

```
views-youtube/
├── backend/
│   ├── agent/              # Automation modules
│   ├── config/             # Configuration
│   ├── utils/              # Utilities
│   └── main.py             # FastAPI entry point
├── frontend/
│   └── src/
│       ├── components/     # React components
│       └── services/       # API client
└── README.md
```

## 🎯 Features

- ✅ Google account management
- ✅ YouTube channel subscription
- ✅ Realistic video watching patterns
- ✅ Context-aware comment generation
- ✅ Like/subscribe automation
- ✅ Real-time dashboard
- ✅ Activity logging

## 🔧 Configuration

Edit `backend/.env`:

```env
TARGET_CHANNEL_URL=https://www.youtube.com/@channel-name
HEADLESS_MODE=false
OPENAI_API_KEY=your-key-here  # Optional
```

## 📚 Learning Resources

This project demonstrates:
- Browser automation with Playwright
- Anti-detection techniques
- REST API design with FastAPI
- React state management
- WebSocket real-time updates

## 📝 License

MIT - Educational purposes only
