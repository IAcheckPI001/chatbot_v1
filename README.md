# Chatbot v1

A full-stack chatbot application with Vue 3 frontend and Python Flask backend.

## Project Structure

```
chatbot_v1/
├── frontend/          # Vue 3 + TypeScript + Vite
│   ├── src/
│   │   └── App.vue    # Main chat interface
│   └── package.json
└── backend/           # Python Flask API
    ├── app.py         # Flask server
    └── requirements.txt
```

## Frontend Setup

1. Navigate to the frontend directory:
```bash
cd frontend
```

2. Install dependencies:
```bash
npm install
```

3. Start the dev server:
```bash
npm run dev
```

The frontend will be available at `http://localhost:5173`

## Backend Setup

1. Navigate to the backend directory:
```bash
cd backend
```

2. Create a virtual environment (optional but recommended):
```bash
# Windows
python -m venv venv
venv\Scripts\activate

# macOS/Linux
python3 -m venv venv
source venv/bin/activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Start the Flask server:
```bash
python app.py
```

The backend API will be available at `http://localhost:5000`

## API Endpoints

### POST `/api/chat`
Send a user message and get relevant responses.

**Request:**
```json
{
  "message": "xin chào"
}
```

**Response:**
```json
{
  "replies": [
    {
      "content": "Response text here...",
      "score": 0.95
    }
  ]
}
```

### GET `/api/health`
Health check endpoint.

**Response:**
```json
{
  "status": "ok",
  "timestamp": "2024-02-26T..."
}
```

## Features

- 💬 **Real-time Chat Interface**: Interactive chat widget with user/bot message separation
- 📊 **Response Table**: Display query results with index, content, and relevance score
- 🔄 **API Integration**: Frontend communicates with Python backend
- ⏳ **Loading States**: Visual feedback while waiting for API responses
- 🎨 **Modern UI**: Clean, responsive design with gradient colors

## How It Works

1. User types a message in the chat input
2. Message is sent to the backend API (`/api/chat`)
3. The backend processes the query and returns relevant responses
4. First response appears in the chat as a bot reply
5. All responses are displayed in the data table below the chat
6. Each response shows content and relevance score

## Customization

### Backend
- Edit `KNOWLEDGE_BASE` in `backend/app.py` to add more responses
- Implement custom matching logic in the `chat()` function for better results

### Frontend
- Modify chat header title in `frontend/src/App.vue`
- Adjust colors in the style section (gradient colors: `#6366f1`, `#9333ea`)
- Change API base URL in `API_BASE_URL` constant if backend runs on a different port

## Technologies

- **Frontend**: Vue 3, TypeScript, Vite, Tailwind-inspired CSS
- **Backend**: Python 3, Flask, Flask-CORS
