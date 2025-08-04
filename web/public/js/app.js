// Main Application Class
class EmotionalAIApp {
    constructor() {
        this.socket = null;
        this.currentConversationId = null;
        this.conversations = new Map();
        this.settings = {
            relationshipMode: 'assistant',
            temperature: 0.7,
            mood: 'neutral',
            evolutionSpeed: 'medium'
        };
        this.isTyping = false;
        this.messageQueue = [];
        
        this.init();
    }

    async init() {
        this.initializeSocket();
        this.bindEvents();
        this.loadSettings();
        await this.loadConversations();
        this.showWelcomeScreen();
    }

    initializeSocket() {
        this.socket = io();
        
        this.socket.on('connect', () => {
            console.log('Connected to server');
            this.updateConnectionStatus(true);
        });

        this.socket.on('disconnect', () => {
            console.log('Disconnected from server');
            this.updateConnectionStatus(false);
        });

        this.socket.on('message', (data) => {
            this.handleIncomingMessage(data);
        });

        this.socket.on('typing', (data) => {
            this.handleTypingIndicator(data);
        });

        this.socket.on('error', (error) => {
            console.error('Socket error:', error);
            this.showError('Connection error occurred');
        });
    }

    bindEvents() {
        // Sidebar events
        document.getElementById('newChatBtn').addEventListener('click', () => {
            this.createNewConversation();
        });

        document.getElementById('settingsBtn').addEventListener('click', () => {
            this.openSettings();
        });

        document.getElementById('sidebarToggle').addEventListener('click', () => {
            this.toggleSidebar();
        });

        // Chat input events
        const messageInput = document.getElementById('messageInput');
        const sendBtn = document.getElementById('sendBtn');

        messageInput.addEventListener('input', (e) => {
            this.handleInputChange(e);
        });

        messageInput.addEventListener('keydown', (e) => {
            if (e.key === 'Enter' && !e.shiftKey) {
                e.preventDefault();
                this.sendMessage();
            }
        });

        sendBtn.addEventListener('click', () => {
            this.sendMessage();
        });

        // Mode selection events
        document.getElementById('modeBtn').addEventListener('click', () => {
            this.openModeSelection();
        });

        // Welcome screen mode cards
        document.querySelectorAll('.mode-card').forEach(card => {
            card.addEventListener('click', () => {
                const mode = card.dataset.mode;
                this.setRelationshipMode(mode);
                this.createNewConversation();
            });
        });

        // Settings modal events
        document.getElementById('closeSettings').addEventListener('click', () => {
            this.closeSettings();
        });

        document.getElementById('saveSettings').addEventListener('click', () => {
            this.saveSettings();
        });

        // Mode modal events
        document.getElementById('closeModeModal').addEventListener('click', () => {
            this.closeModeSelection();
        });

        document.querySelectorAll('.mode-option').forEach(option => {
            option.addEventListener('click', () => {
                document.querySelectorAll('.mode-option').forEach(o => o.classList.remove('selected'));
                option.classList.add('selected');
                this.setRelationshipMode(option.dataset.mode);
            });
        });

        // Modal backdrop clicks
        document.querySelectorAll('.modal').forEach(modal => {
            modal.addEventListener('click', (e) => {
                if (e.target === modal) {
                    modal.classList.remove('active');
                }
            });
        });

        // Settings controls
        document.getElementById('temperatureSlider').addEventListener('input', (e) => {
            document.getElementById('temperatureValue').textContent = e.target.value;
        });
    }

    handleInputChange(e) {
        const input = e.target;
        const charCount = input.value.length;
        const maxChars = 4000;
        
        document.getElementById('charCount').textContent = `${charCount}/${maxChars}`;
        
        // Auto-resize textarea
        input.style.height = 'auto';
        input.style.height = Math.min(input.scrollHeight, 120) + 'px';
        
        // Enable/disable send button
        const sendBtn = document.getElementById('sendBtn');
        sendBtn.disabled = input.value.trim().length === 0;
        
        // Emit typing indicator
        if (this.socket && this.currentConversationId) {
            this.socket.emit('typing', {
                conversationId: this.currentConversationId,
                isTyping: input.value.length > 0
            });
        }
    }

    async sendMessage() {
        const messageInput = document.getElementById('messageInput');
        const message = messageInput.value.trim();
        
        if (!message || this.isTyping) return;
        
        if (!this.currentConversationId) {
            this.createNewConversation();
        }
        
        // Clear input and reset height
        messageInput.value = '';
        messageInput.style.height = 'auto';
        document.getElementById('charCount').textContent = '0/4000';
        document.getElementById('sendBtn').disabled = true;
        
        // Add user message to chat
        this.addMessage({
            id: this.generateId(),
            role: 'user',
            content: message,
            timestamp: new Date().toISOString(),
            conversationId: this.currentConversationId
        });
        
        // Show typing indicator
        this.showTypingIndicator();
        
        // Send to server
        if (this.socket) {
            this.socket.emit('message', {
                conversationId: this.currentConversationId,
                content: message,
                settings: this.settings
            });
        }
        
        // Update conversation in sidebar
        this.updateConversationPreview(this.currentConversationId, message);
    }

    handleIncomingMessage(data) {
        this.hideTypingIndicator();
        
        this.addMessage({
            id: this.generateId(),
            role: 'assistant',
            content: data.content,
            timestamp: new Date().toISOString(),
            conversationId: data.conversationId
        });
        
        // Update conversation preview
        this.updateConversationPreview(data.conversationId, data.content);
    }

    handleTypingIndicator(data) {
        if (data.isTyping) {
            this.showTypingIndicator();
        } else {
            this.hideTypingIndicator();
        }
    }

    addMessage(message) {
        const chatMessages = document.getElementById('chatMessages');
        const welcomeScreen = document.getElementById('welcomeScreen');
        
        // Hide welcome screen if visible
        if (welcomeScreen.style.display !== 'none') {
            welcomeScreen.style.display = 'none';
            chatMessages.style.display = 'block';
        }
        
        const messageEl = this.createMessageElement(message);
        chatMessages.appendChild(messageEl);
        
        // Scroll to bottom
        chatMessages.scrollTop = chatMessages.scrollHeight;
        
        // Store message in conversation
        if (!this.conversations.has(message.conversationId)) {
            this.conversations.set(message.conversationId, {
                id: message.conversationId,
                title: this.generateConversationTitle(message.content),
                messages: [],
                createdAt: message.timestamp,
                updatedAt: message.timestamp
            });
        }
        
        this.conversations.get(message.conversationId).messages.push(message);
        this.conversations.get(message.conversationId).updatedAt = message.timestamp;
    }

    createMessageElement(message) {
        const messageEl = document.createElement('div');
        messageEl.className = `message ${message.role}`;
        messageEl.dataset.messageId = message.id;
        
        const avatarEl = document.createElement('div');
        avatarEl.className = 'message-avatar';
        avatarEl.textContent = message.role === 'user' ? 'U' : 'AI';
        
        const contentEl = document.createElement('div');
        contentEl.className = 'message-content';
        
        const textEl = document.createElement('div');
        textEl.className = 'message-text';
        textEl.innerHTML = this.formatMessageContent(message.content);
        
        const timeEl = document.createElement('div');
        timeEl.className = 'message-time';
        timeEl.textContent = this.formatTime(message.timestamp);
        
        contentEl.appendChild(textEl);
        contentEl.appendChild(timeEl);
        
        messageEl.appendChild(avatarEl);
        messageEl.appendChild(contentEl);
        
        return messageEl;
    }

    formatMessageContent(content) {
        // Basic markdown-like formatting
        return content
            .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
            .replace(/\*(.*?)\*/g, '<em>$1</em>')
            .replace(/`(.*?)`/g, '<code>$1</code>')
            .replace(/\n/g, '<br>');
    }

    formatTime(timestamp) {
        const date = new Date(timestamp);
        return date.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
    }

    showTypingIndicator() {
        const indicator = document.getElementById('typingIndicator');
        indicator.style.display = 'flex';
        this.isTyping = true;
        
        // Scroll to bottom
        const chatMessages = document.getElementById('chatMessages');
        chatMessages.scrollTop = chatMessages.scrollHeight;
    }

    hideTypingIndicator() {
        const indicator = document.getElementById('typingIndicator');
        indicator.style.display = 'none';
        this.isTyping = false;
    }

    createNewConversation() {
        const conversationId = this.generateId();
        this.currentConversationId = conversationId;
        
        // Clear chat messages
        const chatMessages = document.getElementById('chatMessages');
        chatMessages.innerHTML = '';
        chatMessages.style.display = 'none';
        
        // Show welcome screen
        const welcomeScreen = document.getElementById('welcomeScreen');
        welcomeScreen.style.display = 'flex';
        
        // Update chat title
        document.getElementById('chatTitle').textContent = 'New Conversation';
        
        // Create conversation entry
        const conversation = {
            id: conversationId,
            title: 'New Conversation',
            messages: [],
            createdAt: new Date().toISOString(),
            updatedAt: new Date().toISOString()
        };
        
        this.conversations.set(conversationId, conversation);
        this.addConversationToSidebar(conversation);
        this.setActiveConversation(conversationId);
    }

    addConversationToSidebar(conversation) {
        const conversationsList = document.getElementById('conversationsList');
        
        const conversationEl = document.createElement('div');
        conversationEl.className = 'conversation-item';
        conversationEl.dataset.conversationId = conversation.id;
        
        conversationEl.innerHTML = `
            <div class="conversation-title">${conversation.title}</div>
            <div class="conversation-preview">Start a conversation...</div>
            <div class="conversation-time">${this.formatTime(conversation.createdAt)}</div>
        `;
        
        conversationEl.addEventListener('click', () => {
            this.loadConversation(conversation.id);
        });
        
        conversationsList.insertBefore(conversationEl, conversationsList.firstChild);
    }

    updateConversationPreview(conversationId, content) {
        const conversationEl = document.querySelector(`[data-conversation-id="${conversationId}"]`);
        if (conversationEl) {
            const previewEl = conversationEl.querySelector('.conversation-preview');
            const preview = content.length > 50 ? content.substring(0, 50) + '...' : content;
            previewEl.textContent = preview;
            
            const timeEl = conversationEl.querySelector('.conversation-time');
            timeEl.textContent = this.formatTime(new Date().toISOString());
            
            // Move to top
            const conversationsList = document.getElementById('conversationsList');
            conversationsList.insertBefore(conversationEl, conversationsList.firstChild);
        }
        
        // Update conversation title if it's still "New Conversation"
        const conversation = this.conversations.get(conversationId);
        if (conversation && conversation.title === 'New Conversation') {
            const newTitle = this.generateConversationTitle(content);
            conversation.title = newTitle;
            
            const titleEl = conversationEl.querySelector('.conversation-title');
            titleEl.textContent = newTitle;
            
            if (conversationId === this.currentConversationId) {
                document.getElementById('chatTitle').textContent = newTitle;
            }
        }
    }

    generateConversationTitle(content) {
        const words = content.split(' ').slice(0, 4).join(' ');
        return words.length > 30 ? words.substring(0, 30) + '...' : words;
    }

    setActiveConversation(conversationId) {
        document.querySelectorAll('.conversation-item').forEach(item => {
            item.classList.remove('active');
        });
        
        const activeEl = document.querySelector(`[data-conversation-id="${conversationId}"]`);
        if (activeEl) {
            activeEl.classList.add('active');
        }
        
        this.currentConversationId = conversationId;
    }

    async loadConversation(conversationId) {
        const conversation = this.conversations.get(conversationId);
        if (!conversation) return;
        
        this.setActiveConversation(conversationId);
        
        // Update chat title
        document.getElementById('chatTitle').textContent = conversation.title;
        
        // Clear and load messages
        const chatMessages = document.getElementById('chatMessages');
        chatMessages.innerHTML = '';
        
        if (conversation.messages.length === 0) {
            chatMessages.style.display = 'none';
            document.getElementById('welcomeScreen').style.display = 'flex';
        } else {
            chatMessages.style.display = 'block';
            document.getElementById('welcomeScreen').style.display = 'none';
            
            conversation.messages.forEach(message => {
                const messageEl = this.createMessageElement(message);
                chatMessages.appendChild(messageEl);
            });
            
            // Scroll to bottom
            chatMessages.scrollTop = chatMessages.scrollHeight;
        }
    }

    async loadConversations() {
        try {
            const response = await fetch('/api/conversations');
            if (response.ok) {
                const conversations = await response.json();
                conversations.forEach(conv => {
                    this.conversations.set(conv.id, conv);
                    this.addConversationToSidebar(conv);
                });
            }
        } catch (error) {
            console.error('Failed to load conversations:', error);
        }
    }

    showWelcomeScreen() {
        const welcomeScreen = document.getElementById('welcomeScreen');
        const chatMessages = document.getElementById('chatMessages');
        
        welcomeScreen.style.display = 'flex';
        chatMessages.style.display = 'none';
    }

    setRelationshipMode(mode) {
        this.settings.relationshipMode = mode;
        
        const modeDisplay = document.getElementById('relationshipMode');
        const modeNames = {
            assistant: 'Assistant Mode',
            friend: 'Friend Mode',
            therapist: 'Therapist Mode',
            romantic: 'Romantic Mode'
        };
        
        modeDisplay.textContent = modeNames[mode] || 'Assistant Mode';
        
        // Update settings select
        const modeSelect = document.getElementById('relationshipModeSelect');
        modeSelect.value = mode;
        
        // Send to server
        if (this.socket) {
            this.socket.emit('settings', this.settings);
        }
        
        this.saveSettingsToStorage();
    }

    openSettings() {
        const modal = document.getElementById('settingsModal');
        
        // Populate current settings
        document.getElementById('relationshipModeSelect').value = this.settings.relationshipMode;
        document.getElementById('temperatureSlider').value = this.settings.temperature;
        document.getElementById('temperatureValue').textContent = this.settings.temperature;
        document.getElementById('moodSelect').value = this.settings.mood;
        document.getElementById('evolutionSpeed').value = this.settings.evolutionSpeed;
        
        modal.classList.add('active');
    }

    closeSettings() {
        const modal = document.getElementById('settingsModal');
        modal.classList.remove('active');
    }

    saveSettings() {
        this.settings = {
            relationshipMode: document.getElementById('relationshipModeSelect').value,
            temperature: parseFloat(document.getElementById('temperatureSlider').value),
            mood: document.getElementById('moodSelect').value,
            evolutionSpeed: document.getElementById('evolutionSpeed').value
        };
        
        this.setRelationshipMode(this.settings.relationshipMode);
        
        // Send to server
        if (this.socket) {
            this.socket.emit('settings', this.settings);
        }
        
        this.saveSettingsToStorage();
        this.closeSettings();
        
        this.showNotification('Settings saved successfully');
    }

    openModeSelection() {
        const modal = document.getElementById('modeModal');
        
        // Select current mode
        document.querySelectorAll('.mode-option').forEach(option => {
            option.classList.remove('selected');
            if (option.dataset.mode === this.settings.relationshipMode) {
                option.classList.add('selected');
            }
        });
        
        modal.classList.add('active');
    }

    closeModeSelection() {
        const modal = document.getElementById('modeModal');
        modal.classList.remove('active');
    }

    toggleSidebar() {
        const sidebar = document.getElementById('sidebar');
        sidebar.classList.toggle('open');
    }

    loadSettings() {
        const saved = localStorage.getItem('emotionalai_settings');
        if (saved) {
            this.settings = { ...this.settings, ...JSON.parse(saved) };
            this.setRelationshipMode(this.settings.relationshipMode);
        }
    }

    saveSettingsToStorage() {
        localStorage.setItem('emotionalai_settings', JSON.stringify(this.settings));
    }

    updateConnectionStatus(connected) {
        // Could add a connection indicator in the UI
        console.log('Connection status:', connected ? 'Connected' : 'Disconnected');
    }

    showError(message) {
        this.showNotification(message, 'error');
    }

    showNotification(message, type = 'success') {
        // Create a simple notification system
        const notification = document.createElement('div');
        notification.className = `notification ${type}`;
        notification.textContent = message;
        notification.style.cssText = `
            position: fixed;
            top: 20px;
            right: 20px;
            background: ${type === 'error' ? '#e53e3e' : '#38a169'};
            color: white;
            padding: 12px 20px;
            border-radius: 6px;
            z-index: 10001;
            animation: slideIn 0.3s ease;
        `;
        
        document.body.appendChild(notification);
        
        setTimeout(() => {
            notification.style.animation = 'slideOut 0.3s ease';
            setTimeout(() => notification.remove(), 300);
        }, 3000);
    }

    generateId() {
        return Date.now().toString(36) + Math.random().toString(36).substr(2);
    }
}

// Initialize the application when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    window.emotionalAI = new EmotionalAIApp();
});

// Add CSS for notifications
const style = document.createElement('style');
style.textContent = `
    @keyframes slideIn {
        from {
            transform: translateX(100%);
            opacity: 0;
        }
        to {
            transform: translateX(0);
            opacity: 1;
        }
    }
    
    @keyframes slideOut {
        from {
            transform: translateX(0);
            opacity: 1;
        }
        to {
            transform: translateX(100%);
            opacity: 0;
        }
    }
`;
document.head.appendChild(style);
