const express = require('express');
const http = require('http');
const socketIo = require('socket.io');
const cors = require('cors');
const helmet = require('helmet');
const rateLimit = require('express-rate-limit');
const { v4: uuidv4 } = require('uuid');
const axios = require('axios');
const path = require('path');
require('dotenv').config();

const app = express();
const server = http.createServer(app);
const io = socketIo(server, {
  cors: {
    origin: process.env.FRONTEND_URL || "http://localhost:3000",
    methods: ["GET", "POST"]
  }
});

// Middleware
app.use(helmet({
  contentSecurityPolicy: {
    directives: {
      defaultSrc: ["'self'"],
      styleSrc: ["'self'", "'unsafe-inline'"],
      scriptSrc: ["'self'"],
      imgSrc: ["'self'", "data:", "https:"],
      connectSrc: ["'self'", "ws:", "wss:"]
    }
  }
}));

app.use(cors());
app.use(express.json({ limit: '10mb' }));
app.use(express.urlencoded({ extended: true }));

// Rate limiting
const limiter = rateLimit({
  windowMs: 15 * 60 * 1000, // 15 minutes
  max: 100, // limit each IP to 100 requests per windowMs
  message: 'Too many requests from this IP, please try again later.'
});
app.use('/api/', limiter);

// Serve static files
app.use(express.static(path.join(__dirname, 'public')));

// Store active sessions and conversations
const activeSessions = new Map();
const conversations = new Map();

// API Routes
app.get('/api/health', (req, res) => {
  res.json({ status: 'healthy', timestamp: new Date().toISOString() });
});

// Get user conversations/threads
app.get('/api/conversations/:userId', (req, res) => {
  const userId = req.params.userId;
  const userConversations = Array.from(conversations.values())
    .filter(conv => conv.userId === userId)
    .map(conv => ({
      id: conv.id,
      title: conv.title,
      lastMessage: conv.lastMessage,
      timestamp: conv.timestamp,
      messageCount: conv.messages.length
    }));
  
  res.json(userConversations);
});

// Get specific conversation
app.get('/api/conversations/:userId/:threadId', (req, res) => {
  const { userId, threadId } = req.params;
  const conversationKey = `${userId}_${threadId}`;
  const conversation = conversations.get(conversationKey);
  
  if (!conversation) {
    return res.status(404).json({ error: 'Conversation not found' });
  }
  
  res.json(conversation);
});

// Create new conversation
app.post('/api/conversations/:userId', (req, res) => {
  const userId = req.params.userId;
  const threadId = uuidv4();
  const { title } = req.body;
  
  const conversation = {
    id: threadId,
    userId: userId,
    title: title || 'New Conversation',
    messages: [],
    timestamp: new Date().toISOString(),
    lastMessage: null,
    settings: {
      relationshipMode: 'assistant',
      temperature: 0.7,
      mood: 'neutral'
    }
  };
  
  const conversationKey = `${userId}_${threadId}`;
  conversations.set(conversationKey, conversation);
  
  res.json({ threadId, conversation });
});

// Update conversation settings
app.put('/api/conversations/:userId/:threadId/settings', (req, res) => {
  const { userId, threadId } = req.params;
  const conversationKey = `${userId}_${threadId}`;
  const conversation = conversations.get(conversationKey);
  
  if (!conversation) {
    return res.status(404).json({ error: 'Conversation not found' });
  }
  
  conversation.settings = { ...conversation.settings, ...req.body };
  conversations.set(conversationKey, conversation);
  
  res.json({ success: true, settings: conversation.settings });
});

// Socket.IO connection handling
io.on('connection', (socket) => {
  console.log('User connected:', socket.id);
  
  // Join user to their room
  socket.on('join', (userId) => {
    socket.join(userId);
    activeSessions.set(socket.id, userId);
    console.log(`User ${userId} joined room`);
  });
  
  // Handle new message
  socket.on('message', async (data) => {
    const { userId, threadId, message, messageId } = data;
    
    try {
      // Store user message
      const conversationKey = `${userId}_${threadId}`;
      let conversation = conversations.get(conversationKey);
      
      if (!conversation) {
        // Create conversation if it doesn't exist
        conversation = {
          id: threadId,
          userId: userId,
          title: message.substring(0, 50) + '...',
          messages: [],
          timestamp: new Date().toISOString(),
          lastMessage: null,
          settings: {
            relationshipMode: 'assistant',
            temperature: 0.7,
            mood: 'neutral'
          }
        };
        conversations.set(conversationKey, conversation);
      }
      
      // Add user message
      const userMessage = {
        id: messageId || uuidv4(),
        role: 'user',
        content: message,
        timestamp: new Date().toISOString()
      };
      
      conversation.messages.push(userMessage);
      conversation.lastMessage = message;
      conversation.timestamp = new Date().toISOString();
      
      // Emit user message to room
      io.to(userId).emit('messageReceived', {
        threadId,
        message: userMessage
      });
      
      // Send typing indicator
      io.to(userId).emit('typing', { threadId, isTyping: true });
      
      // Call Emotional AI backend
      const aiResponse = await callEmotionalAI(userId, threadId, message, conversation.settings);
      
      // Add AI response
      const aiMessage = {
        id: uuidv4(),
        role: 'assistant',
        content: aiResponse,
        timestamp: new Date().toISOString()
      };
      
      conversation.messages.push(aiMessage);
      conversations.set(conversationKey, conversation);
      
      // Stop typing and send response
      io.to(userId).emit('typing', { threadId, isTyping: false });
      io.to(userId).emit('messageReceived', {
        threadId,
        message: aiMessage
      });
      
    } catch (error) {
      console.error('Error processing message:', error);
      io.to(userId).emit('error', {
        threadId,
        error: 'Failed to process message'
      });
    }
  });
  
  // Handle conversation settings update
  socket.on('updateSettings', (data) => {
    const { userId, threadId, settings } = data;
    const conversationKey = `${userId}_${threadId}`;
    const conversation = conversations.get(conversationKey);
    
    if (conversation) {
      conversation.settings = { ...conversation.settings, ...settings };
      conversations.set(conversationKey, conversation);
      
      // Notify about settings update
      io.to(userId).emit('settingsUpdated', {
        threadId,
        settings: conversation.settings
      });
    }
  });
  
  socket.on('disconnect', () => {
    const userId = activeSessions.get(socket.id);
    if (userId) {
      activeSessions.delete(socket.id);
      console.log(`User ${userId} disconnected`);
    }
  });
});

// Function to call Emotional AI backend
async function callEmotionalAI(userId, threadId, message, settings) {
  try {
    const backendUrl = process.env.EMOTIONAL_AI_BACKEND || 'http://localhost:8000';
    
    const response = await axios.post(`${backendUrl}/api/message`, {
      user_id: userId,
      thread_id: threadId,
      message: message,
      settings: settings
    }, {
      timeout: 30000,
      headers: {
        'Content-Type': 'application/json'
      }
    });
    
    return response.data.response || 'I apologize, but I couldn\'t process your message right now.';
    
  } catch (error) {
    console.error('Error calling Emotional AI backend:', error.message);
    
    // Fallback response
    return 'I\'m having trouble connecting to my core systems right now. Please try again in a moment.';
  }
}

// Serve the main app
app.get('*', (req, res) => {
  res.sendFile(path.join(__dirname, 'public', 'index.html'));
});

// Start server
const PORT = process.env.PORT || 3000;
server.listen(PORT, () => {
  console.log(`Emotional AI Web Interface running on port ${PORT}`);
  console.log(`Environment: ${process.env.NODE_ENV || 'development'}`);
});

module.exports = { app, server, io };
