# Core1 AI Gateway

A minimal React frontend with Node.js backend for chatting with both cloud (OpenRouter) and local (Ollama) AI models.

## Features

- 🌐 **Cloud Models**: GPT-4, Claude 3, Llama 2 via OpenRouter
- 🖥️ **Local Models**: Dolphin Mixtral, Kimi K2, Code Llama via Ollama
- 💬 **Real-time Chat**: Clean, responsive chat interface
- 🎛️ **Model Switching**: Toggle between cloud and local models
- 🔧 **Status Monitoring**: Backend health and configuration status

## Setup

### 1. Install Dependencies

```bash
cd core1-gateway
npm install
```

### 2. Configure Environment

Edit `.env` file:

```env
OPENROUTER_KEY=your_openrouter_api_key_here
LOCAL_MODEL_API=http://localhost:11434
```

### 3. Start the Application

```bash
# Start both backend and frontend
npm start

# Or start them separately:
npm run start-backend  # Backend on port 5000
npm run dev            # Frontend on port 3000
```

## Usage

1. **Frontend**: Open http://localhost:3000
2. **Backend API**: Available at http://localhost:5000

### Chat Interface

- Type your message and press Enter to send
- Use Shift+Enter for new lines
- Toggle between cloud and local models
- Select different models from the dropdown
- Clear chat history with the Clear button

### API Endpoints

- `POST /api/chat` - Send chat messages
- `GET /api/models/cloud` - List available cloud models
- `GET /api/models/local` - List available local models
- `GET /api/status` - Backend health check

## Architecture

```
┌─────────────────┐    ┌─────────────────┐    ┌──────────────────┐
│   React Frontend │    │  Node.js Server │    │   AI Providers   │
│   (Port 3000)   │───▶│   (Port 5000)   │───▶│  OpenRouter/     │
│                 │    │                 │    │  Ollama          │
└─────────────────┘    └─────────────────┘    └──────────────────┘
```

## Dependencies

### Frontend
- React 18
- Vite (build tool)
- Tailwind CSS (styling)
- Axios (HTTP client)

### Backend
- Express.js (web server)
- Axios (API requests)
- CORS (cross-origin requests)
- dotenv (environment variables)

## Development

```bash
# Frontend development server
npm run dev

# Backend development (with auto-restart)
npm run start-backend

# Build for production
npm run build

# Preview production build
npm run preview
```

## Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `OPENROUTER_KEY` | OpenRouter API key | Required for cloud models |
| `LOCAL_MODEL_API` | Local Ollama endpoint | `http://localhost:11434` |
| `PORT` | Backend server port | `5000` |

## Troubleshooting

### Backend Connection Issues
- Ensure backend is running on port 5000
- Check `.env` configuration
- Verify OpenRouter API key is valid

### Local Models Not Working
- Ensure Ollama is running on the configured port
- Check available models with `ollama list`
- Verify `LOCAL_MODEL_API` endpoint is correct

### Frontend Build Issues
- Clear node_modules and reinstall: `rm -rf node_modules package-lock.json && npm install`
- Ensure Node.js version is 16+ 

## License

MIT
