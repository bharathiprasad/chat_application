class ChatApp {
    constructor() {
        this.socket = null;
        this.currentRoom = null;
        this.username = null;
        this.typingTimer = null;
        this.connectionStatus = 'disconnected';
        
        this.initializeElements();
        this.bindEvents();
        this.initializeSocket();
        this.createConnectionStatus();
    }

    initializeElements() {
        this.usernameInput = document.getElementById('usernameInput');
        this.setUsernameBtn = document.getElementById('setUsernameBtn');
        this.userStatus = document.getElementById('userStatus');
        this.messageInput = document.getElementById('messageInput');
        this.sendButton = document.getElementById('sendButton');
        this.messagesContainer = document.getElementById('messagesContainer');
        this.roomsList = document.getElementById('roomsList');
        this.chatTitle = document.getElementById('chatTitle');
        this.onlineUsers = document.getElementById('onlineUsers');
        this.welcomeScreen = document.getElementById('welcomeScreen');
        this.chatArea = document.getElementById('chatArea');
        this.errorMessage = document.getElementById('errorMessage');
        this.typingIndicator = document.getElementById('typingIndicator');
    }

    bindEvents() {
        this.usernameInput.addEventListener('keypress', (e) => {
            if (e.key === 'Enter') {
                this.setUsername();
            }
        });

        this.setUsernameBtn.addEventListener('click', () => {
            this.setUsername();
        });

        this.messageInput.addEventListener('keypress', (e) => {
            if (e.key === 'Enter') {
                this.sendMessage();
            }
        });

        this.messageInput.addEventListener('input', () => {
            this.handleTyping();
        });

        this.sendButton.addEventListener('click', () => {
            this.sendMessage();
        });

        // Handle page visibility for better UX
        document.addEventListener('visibilitychange', () => {
            if (document.hidden) {
                this.handlePageHidden();
            } else {
                this.handlePageVisible();
            }
        });
    }

    createConnectionStatus() {
        if (!CONFIG.UI_SETTINGS.SHOW_CONNECTION_STATUS) return;
        
        this.connectionStatusElement = document.createElement('div');
        this.connectionStatusElement.className = 'connection-status disconnected';
        this.connectionStatusElement.textContent = 'Disconnected';
        document.body.appendChild(this.connectionStatusElement);
    }

    updateConnectionStatus(status) {
        this.connectionStatus = status;
        
        if (!this.connectionStatusElement) return;
        
        this.connectionStatusElement.className = `connection-status ${status}`;
        
        switch (status) {
            case 'connected':
                this.connectionStatusElement.textContent = 'Connected';
                break;
            case 'connecting':
                this.connectionStatusElement.textContent = 'Connecting...';
                break;
            case 'disconnected':
                this.connectionStatusElement.textContent = 'Disconnected';
                break;
            case 'reconnecting':
                this.connectionStatusElement.textContent = 'Reconnecting...';
                break;
        }
    }

    initializeSocket() {
        this.updateConnectionStatus('connecting');
        
        this.socket = io(CONFIG.SERVER_URL, CONFIG.SOCKET_OPTIONS);
        this.setupSocketListeners();
    }

    setupSocketListeners() {
        this.socket.on('connect', () => {
            console.log('Connected to server');
            this.updateConnectionStatus('connected');
            this.socket.emit('get_rooms');
        });

        this.socket.on('disconnect', (reason) => {
            console.log('Disconnected from server:', reason);
            this.updateConnectionStatus('disconnected');
            this.showError('Disconnected from server');
        });

        this.socket.on('reconnect_attempt', () => {
            console.log('Attempting to reconnect...');
            this.updateConnectionStatus('reconnecting');
        });

        this.socket.on('reconnect', () => {
            console.log('Reconnected to server');
            this.updateConnectionStatus('connected');
            this.hideError();
            // Re-join current room if user was in one
            if (this.currentRoom && this.username) {
                this.socket.emit('join_room', { room: this.currentRoom });
            }
        });

        this.socket.on('connect_error', (error) => {
            console.error('Connection error:', error);
            this.updateConnectionStatus('disconnected');
            this.showError('Failed to connect to server');
        });

        this.socket.on('username_set', (data) => {
            this.username = data.username;
            this.usernameInput.disabled = true;
            this.setUsernameBtn.disabled = true;
            this.setUsernameBtn.textContent = 'Username Set';
            this.userStatus.textContent = `Logged in as: ${this.username}`;
            this.userStatus.style.display = 'block';
            this.hideError();
            this.socket.emit('get_rooms');
            console.log('Username set successfully:', this.username);
        });

        this.socket.on('rooms_list', (rooms) => {
            this.displayRooms(rooms);
        });

        this.socket.on('joined_room', (data) => {
            this.currentRoom = data.room;
            this.chatTitle.textContent = data.room_name;
            this.onlineUsers.textContent = `${data.users.length} users online`;
            this.displayMessages(data.messages);
            this.showChatArea();
            this.messageInput.disabled = false;
            this.sendButton.disabled = false;
            console.log('Joined room:', data.room);
        });

        this.socket.on('new_message', (message) => {
            this.displayMessage(message);
            this.playNotificationSound();
        });

        this.socket.on('user_joined', (data) => {
            this.addSystemMessage(`${data.username} joined the room`);
            this.onlineUsers.textContent = `${data.user_count} users online`;
        });

        this.socket.on('user_left', (data) => {
            this.addSystemMessage(`${data.username} left the room`);
            this.onlineUsers.textContent = `${data.user_count} users online`;
        });

        this.socket.on('user_typing', (data) => {
            if (CONFIG.UI_SETTINGS.SHOW_TYPING_INDICATOR) {
                if (data.typing) {
                    this.typingIndicator.textContent = `${data.username} is typing...`;
                } else {
                    this.typingIndicator.textContent = '';
                }
            }
        });

        this.socket.on('error', (data) => {
            this.showError(data.message);
            console.error('Socket error:', data.message);
        });
    }

    setUsername() {
        const username = this.usernameInput.value.trim();
        
        if (!username) {
            this.showError('Please enter a username');
            return;
        }

        if (username.length < 2) {
            this.showError('Username must be at least 2 characters long');
            return;
        }

        if (username.length > 20) {
            this.showError('Username must be less than 20 characters');
            return;
        }

        // Check for valid characters
        if (!/^[a-zA-Z0-9_-]+$/.test(username)) {
            this.showError('Username can only contain letters, numbers, underscores, and hyphens');
            return;
        }

        console.log('Setting username:', username);
        this.socket.emit('set_username', { username });
    }

    joinRoom(roomId) {
        if (!this.username) {
            this.showError('Please set a username first');
            return;
        }

        if (this.connectionStatus !== 'connected') {
            this.showError('Not connected to server');
            return;
        }

        console.log('Joining room:', roomId);
        this.socket.emit('join_room', { room: roomId });
        this.updateActiveRoom(roomId);
    }

    sendMessage() {
        const message = this.messageInput.value.trim();
        
        if (!message) return;
        
        if (message.length > CONFIG.APP_SETTINGS.MAX_MESSAGE_LENGTH) {
            this.showError(`Message too long. Maximum ${CONFIG.APP_SETTINGS.MAX_MESSAGE_LENGTH} characters allowed.`);
            return;
        }

        if (!this.currentRoom) {
            this.showError('Please join a room first');
            return;
        }

        if (this.connectionStatus !== 'connected') {
            this.showError('Not connected to server');
            return;
        }

        this.socket.emit('send_message', { message });
        this.messageInput.value = '';
        this.socket.emit('typing', { typing: false });
    }

    handleTyping() {
        if (!this.currentRoom || !CONFIG.UI_SETTINGS.SHOW_TYPING_INDICATOR) return;

        this.socket.emit('typing', { typing: true });
        
        clearTimeout(this.typingTimer);
        this.typingTimer = setTimeout(() => {
            this.socket.emit('typing', { typing: false });
        }, CONFIG.APP_SETTINGS.TYPING_TIMEOUT);
    }

    displayRooms(rooms) {
        this.roomsList.innerHTML = '';
        Object.entries(rooms).forEach(([roomId, roomData]) => {
            const roomElement = document.createElement('div');
            roomElement.className = 'room-item';
            roomElement.innerHTML = `
                <span>${roomData.name}</span>
                <span class="room-count">${roomData.user_count}</span>
            `;
            roomElement.addEventListener('click', () => this.joinRoom(roomId));
            this.roomsList.appendChild(roomElement);
        });
    }

    updateActiveRoom(roomId) {
        document.querySelectorAll('.room-item').forEach(item => {
            item.classList.remove('active');
        });
        // Find the clicked room and mark it active
        document.querySelectorAll('.room-item').forEach(item => {
            if (item.textContent.includes(this.getRoomName(roomId))) {
                item.classList.add('active');
            }
        });
    }

    getRoomName(roomId) {
        const roomNames = {
            'general': 'General',
            'tech': 'Tech Talk',
            'random': 'Random'
        };
        return roomNames[roomId] || roomId;
    }

    displayMessages(messages) {
        this.messagesContainer.innerHTML = '';
        messages.forEach(message => this.displayMessage(message));
    }

    displayMessage(message) {
        const messageElement = document.createElement('div');
        messageElement.className = `message ${message.username === this.username ? 'own' : ''}`;
        
        let timestampHtml = '';
        if (CONFIG.UI_SETTINGS.SHOW_TIMESTAMPS) {
            timestampHtml = `<span class="timestamp">${message.timestamp}</span>`;
        }

        messageElement.innerHTML = `
            <div class="message-header">
                <span class="username">${this.escapeHtml(message.username)}</span>
                ${timestampHtml}
            </div>
            <div class="message-text">${this.escapeHtml(message.message)}</div>
        `;
        
        this.messagesContainer.appendChild(messageElement);
        this.scrollToBottom();
    }

    addSystemMessage(text) {
        const messageElement = document.createElement('div');
        messageElement.className = 'system-message';
        messageElement.textContent = text;
        this.messagesContainer.appendChild(messageElement);
        this.scrollToBottom();
    }

    scrollToBottom() {
        const container = this.messagesContainer;
        const shouldScroll = container.scrollTop + container.clientHeight >= 
                           container.scrollHeight - CONFIG.APP_SETTINGS.AUTO_SCROLL_THRESHOLD;
        
        if (shouldScroll) {
            container.scrollTop = container.scrollHeight;
        }
    }

    showChatArea() {
        this.welcomeScreen.style.display = 'none';
        this.chatArea.style.display = 'flex';
    }

    showError(message) {
        this.errorMessage.textContent = message;
        this.errorMessage.style.display = 'block';
        setTimeout(() => this.hideError(), 5000);
    }

    hideError() {
        this.errorMessage.style.display = 'none';
    }

    escapeHtml(text) {
        const div = document.createElement('div');
        div.textContent = text;
        return div.innerHTML;
    }

    playNotificationSound() {
        // Simple notification sound (you can replace with actual audio file)
        if (document.hidden && 'Notification' in window) {
            // Only show notification if page is hidden
            this.showNotification('New message in chat');
        }
    }

    showNotification(message) {
        if (Notification.permission === 'granted') {
            new Notification('Chat App', {
                body: message,
                icon: '/favicon.ico',
                tag: 'chat-message'
            });
        } else if (Notification.permission !== 'denied') {
            Notification.requestPermission().then(permission => {
                if (permission === 'granted') {
                    new Notification('Chat App', {
                        body: message,
                        icon: '/favicon.ico',
                        tag: 'chat-message'
                    });
                }
            });
        }
    }

    handlePageHidden() {
        // Reduce socket activity when page is hidden
        if (this.socket) {
            this.socket.emit('typing', { typing: false });
        }
    }

    handlePageVisible() {
        // Resume normal activity when page becomes visible
        if (this.socket && this.connectionStatus === 'disconnected') {
            this.socket.connect();
        }
    }

    // Public methods for external use
    getCurrentRoom() {
        return this.currentRoom;
    }

    getUsername() {
        return this.username;
    }

    isConnected() {
        return this.connectionStatus === 'connected';
    }

    // Cleanup method
    destroy() {
        if (this.socket) {
            this.socket.disconnect();
        }
        if (this.typingTimer) {
            clearTimeout(this.typingTimer);
        }
        if (this.connectionStatusElement) {
            this.connectionStatusElement.remove();
        }
    }
}

// Initialize the chat app when the page loads
document.addEventListener('DOMContentLoaded', () => {
    // Request notification permission on page load
    if ('Notification' in window && Notification.permission === 'default') {
        Notification.requestPermission();
    }
    
    // Initialize the chat application
    window.chatApp = new ChatApp();
    
    // Handle page unload
    window.addEventListener('beforeunload', () => {
        if (window.chatApp) {
            window.chatApp.destroy();
        }
    });
});

// Export for debugging purposes
window.ChatApp = ChatApp;