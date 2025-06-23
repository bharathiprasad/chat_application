from flask import Flask, request, session
from flask_socketio import SocketIO, emit, join_room, leave_room, rooms
import uuid
from datetime import datetime
import json

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your-secret-key-here'
socketio = SocketIO(app, cors_allowed_origins="*")

# In-memory storage for chat rooms and messages
chat_rooms = {
    'general': {
        'name': 'General',
        'messages': [],
        'users': set()
    },
    'tech': {
        'name': 'Tech Talk',
        'messages': [],
        'users': set()
    },
    'random': {
        'name': 'Random',
        'messages': [],
        'users': set()
    }
}

# Store connected users
connected_users = {}

@app.route('/')
def index():
    return '''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Real-time Chat App</title>
    <script src="https://cdnjs.cloudflare.com/ajax/libs/socket.io/4.7.2/socket.io.js"></script>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }

        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            height: 100vh;
            display: flex;
            align-items: center;
            justify-content: center;
        }

        .chat-container {
            width: 95%;
            max-width: 1200px;
            height: 90vh;
            background: white;
            border-radius: 15px;
            box-shadow: 0 20px 40px rgba(0,0,0,0.1);
            display: flex;
            overflow: hidden;
        }

        .sidebar {
            width: 280px;
            background: #2c3e50;
            color: white;
            display: flex;
            flex-direction: column;
        }

        .user-info {
            padding: 20px;
            background: #34495e;
            border-bottom: 1px solid #3d566e;
        }

        .username-input {
            width: 100%;
            padding: 10px;
            border: none;
            border-radius: 8px;
            margin-top: 10px;
            font-size: 14px;
        }

        .set-username-btn {
            width: 100%;
            padding: 10px;
            background: #27ae60;
            color: white;
            border: none;
            border-radius: 8px;
            margin-top: 10px;
            cursor: pointer;
            font-size: 14px;
        }

        .set-username-btn:hover {
            background: #219a52;
        }

        .set-username-btn:disabled {
            background: #7f8c8d;
            cursor: not-allowed;
        }

        .rooms-section {
            flex: 1;
            padding: 20px;
        }

        .room-item {
            padding: 12px 15px;
            margin: 5px 0;
            background: #34495e;
            border-radius: 8px;
            cursor: pointer;
            transition: background 0.3s;
            display: flex;
            justify-content: space-between;
            align-items: center;
        }

        .room-item:hover {
            background: #4a6741;
        }

        .room-item.active {
            background: #27ae60;
        }

        .room-count {
            background: #e74c3c;
            color: white;
            border-radius: 50%;
            padding: 2px 8px;
            font-size: 12px;
        }

        .main-chat {
            flex: 1;
            display: flex;
            flex-direction: column;
        }

        .chat-header {
            padding: 20px;
            background: #ecf0f1;
            border-bottom: 1px solid #ddd;
            display: flex;
            justify-content: space-between;
            align-items: center;
        }

        .chat-title {
            font-size: 20px;
            font-weight: bold;
            color: #2c3e50;
        }

        .online-users {
            font-size: 14px;
            color: #7f8c8d;
        }

        .messages-container {
            flex: 1;
            overflow-y: auto;
            padding: 20px;
            background: #f8f9fa;
        }

        .message {
            margin-bottom: 15px;
            padding: 12px 15px;
            background: white;
            border-radius: 10px;
            box-shadow: 0 2px 5px rgba(0,0,0,0.1);
            animation: fadeIn 0.3s ease-in;
        }

        .message.own {
            background: #3498db;
            color: white;
            margin-left: 50px;
        }

        .message-header {
            display: flex;
            justify-content: space-between;
            margin-bottom: 5px;
            font-size: 12px;
        }

        .message.own .message-header {
            color: #ecf0f1;
        }

        .username {
            font-weight: bold;
            color: #2c3e50;
        }

        .message.own .username {
            color: #ecf0f1;
        }

        .timestamp {
            color: #7f8c8d;
        }

        .message.own .timestamp {
            color: #bdc3c7;
        }

        .message-text {
            font-size: 14px;
            line-height: 1.4;
            word-wrap: break-word;
        }

        .system-message {
            text-align: center;
            color: #7f8c8d;
            font-style: italic;
            margin: 10px 0;
            font-size: 13px;
        }

        .typing-indicator {
            color: #7f8c8d;
            font-style: italic;
            font-size: 13px;
            margin-left: 15px;
            min-height: 20px;
        }

        .message-input-container {
            padding: 20px;
            background: white;
            border-top: 1px solid #ddd;
            display: flex;
            gap: 10px;
        }

        .message-input {
            flex: 1;
            padding: 12px 15px;
            border: 2px solid #ddd;
            border-radius: 25px;
            font-size: 14px;
            outline: none;
            transition: border-color 0.3s;
        }

        .message-input:focus {
            border-color: #3498db;
        }

        .send-button {
            padding: 12px 20px;
            background: #3498db;
            color: white;
            border: none;
            border-radius: 25px;
            cursor: pointer;
            font-weight: bold;
            transition: background 0.3s;
        }

        .send-button:hover:not(:disabled) {
            background: #2980b9;
        }

        .send-button:disabled {
            background: #bdc3c7;
            cursor: not-allowed;
        }

        .welcome-screen {
            display: flex;
            flex-direction: column;
            align-items: center;
            justify-content: center;
            flex: 1;
            color: #7f8c8d;
            text-align: center;
        }

        .welcome-screen h2 {
            margin-bottom: 10px;
            color: #2c3e50;
        }

        .error-message {
            background: #e74c3c;
            color: white;
            padding: 10px;
            border-radius: 5px;
            margin: 10px 0;
            text-align: center;
        }

        .user-status {
            margin-top: 10px;
            padding: 8px;
            background: #27ae60;
            border-radius: 5px;
            font-size: 13px;
        }

        @keyframes fadeIn {
            from { opacity: 0; transform: translateY(10px); }
            to { opacity: 1; transform: translateY(0); }
        }

        @media (max-width: 768px) {
            .chat-container {
                width: 100%;
                height: 100vh;
                border-radius: 0;
            }
            
            .sidebar {
                width: 250px;
            }
            
            .message.own {
                margin-left: 20px;
            }
        }
    </style>
</head>
<body>
    <div class="chat-container">
        <div class="sidebar">
            <div class="user-info">
                <h3>Welcome!</h3>
                <input type="text" id="usernameInput" placeholder="Enter your username..." class="username-input">
                <button id="setUsernameBtn" class="set-username-btn">Set Username</button>
                <div id="userStatus" class="user-status" style="display: none;"></div>
                <div id="errorMessage" class="error-message" style="display: none;"></div>
            </div>
            <div class="rooms-section">
                <h4 style="margin-bottom: 15px;">Chat Rooms</h4>
                <div id="roomsList"></div>
            </div>
        </div>

        <div class="main-chat">
            <div class="chat-header">
                <div class="chat-title" id="chatTitle">Select a room to start chatting</div>
                <div class="online-users" id="onlineUsers"></div>
            </div>

            <div id="welcomeScreen" class="welcome-screen">
                <h2>Welcome to Real-time Chat!</h2>
                <p>Enter your username and select a room to start chatting.</p>
            </div>

            <div id="chatArea" style="display: none; flex: 1; display: flex; flex-direction: column;">
                <div class="messages-container" id="messagesContainer"></div>
                <div class="typing-indicator" id="typingIndicator"></div>
                <div class="message-input-container">
                    <input type="text" id="messageInput" placeholder="Type your message..." class="message-input">
                    <button id="sendButton" class="send-button" disabled>Send</button>
                </div>
            </div>
        </div>
    </div>

    <script>
        class ChatApp {
            constructor() {
                this.socket = io();
                this.currentRoom = null;
                this.username = null;
                this.typingTimer = null;
                
                this.initializeElements();
                this.bindEvents();
                this.setupSocketListeners();
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
            }

            setupSocketListeners() {
                this.socket.on('connect', () => {
                    console.log('Connected to server');
                    this.socket.emit('get_rooms');
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
                    if (data.typing) {
                        this.typingIndicator.textContent = `${data.username} is typing...`;
                    } else {
                        this.typingIndicator.textContent = '';
                    }
                });

                this.socket.on('error', (data) => {
                    this.showError(data.message);
                    console.error('Socket error:', data.message);
                });

                this.socket.on('disconnect', () => {
                    console.log('Disconnected from server');
                    this.showError('Disconnected from server');
                });
            }

            setUsername() {
                const username = this.usernameInput.value.trim();
                if (username) {
                    console.log('Setting username:', username);
                    this.socket.emit('set_username', { username });
                } else {
                    this.showError('Please enter a username');
                }
            }

            joinRoom(roomId) {
                if (this.username) {
                    console.log('Joining room:', roomId);
                    this.socket.emit('join_room', { room: roomId });
                    this.updateActiveRoom(roomId);
                } else {
                    this.showError('Please set a username first');
                }
            }

            sendMessage() {
                const message = this.messageInput.value.trim();
                if (message && this.currentRoom) {
                    this.socket.emit('send_message', { message });
                    this.messageInput.value = '';
                    this.socket.emit('typing', { typing: false });
                }
            }

            handleTyping() {
                if (!this.currentRoom) return;

                this.socket.emit('typing', { typing: true });
                
                clearTimeout(this.typingTimer);
                this.typingTimer = setTimeout(() => {
                    this.socket.emit('typing', { typing: false });
                }, 1000);
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
                messageElement.innerHTML = `
                    <div class="message-header">
                        <span class="username">${message.username}</span>
                        <span class="timestamp">${message.timestamp}</span>
                    </div>
                    <div class="message-text">${this.escapeHtml(message.message)}</div>
                `;
                this.messagesContainer.appendChild(messageElement);
                this.messagesContainer.scrollTop = this.messagesContainer.scrollHeight;
            }

            addSystemMessage(text) {
                const messageElement = document.createElement('div');
                messageElement.className = 'system-message';
                messageElement.textContent = text;
                this.messagesContainer.appendChild(messageElement);
                this.messagesContainer.scrollTop = this.messagesContainer.scrollHeight;
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
        }

        // Initialize the chat app when the page loads
        document.addEventListener('DOMContentLoaded', () => {
            new ChatApp();
        });
    </script>
</body>
</html>'''

@socketio.on('connect')
def handle_connect():
    user_id = str(uuid.uuid4())
    session['user_id'] = user_id
    connected_users[user_id] = {
        'username': None,
        'current_room': None,
        'connected_at': datetime.now()
    }
    print(f'User {user_id} connected')
    print(f'Total connected users: {len(connected_users)}')

@socketio.on('disconnect')
def handle_disconnect():
    user_id = session.get('user_id')
    if user_id in connected_users:
        user_data = connected_users[user_id]
        if user_data['current_room']:
            leave_room(user_data['current_room'])
            if user_data['current_room'] in chat_rooms:
                chat_rooms[user_data['current_room']]['users'].discard(user_data['username'])
                # Notify room about user leaving
                socketio.emit('user_left', {
                    'username': user_data['username'],
                    'room': user_data['current_room'],
                    'user_count': len(chat_rooms[user_data['current_room']]['users'])
                }, room=user_data['current_room'])
        
        del connected_users[user_id]
    print(f'User {user_id} disconnected')

@socketio.on('set_username')
def handle_set_username(data):
    user_id = session.get('user_id')
    username = data['username'].strip()
    
    print(f'Setting username for user {user_id}: {username}')
    
    if not username:
        print('Username is empty')
        emit('error', {'message': 'Username cannot be empty'})
        return
    
    if user_id not in connected_users:
        print(f'User {user_id} not found in connected_users')
        emit('error', {'message': 'User session not found. Please refresh the page.'})
        return
    
    # Check if username is already taken
    for uid, user_data in connected_users.items():
        if user_data['username'] == username and uid != user_id:
            print(f'Username {username} already taken by user {uid}')
            emit('error', {'message': 'Username already taken'})
            return
    
    connected_users[user_id]['username'] = username
    print(f'Username set successfully for user {user_id}: {username}')
    print(f'Connected users: {[(uid, data["username"]) for uid, data in connected_users.items()]}')
    emit('username_set', {'username': username})

@socketio.on('join_room')
def handle_join_room(data):
    user_id = session.get('user_id')
    room = data['room']
    
    if user_id not in connected_users or not connected_users[user_id]['username']:
        emit('error', {'message': 'Please set a username first'})
        return
    
    username = connected_users[user_id]['username']
    current_room = connected_users[user_id]['current_room']
    
    # Leave current room if in one
    if current_room:
        leave_room(current_room)
        chat_rooms[current_room]['users'].discard(username)
        socketio.emit('user_left', {
            'username': username,
            'room': current_room,
            'user_count': len(chat_rooms[current_room]['users'])
        }, room=current_room)
    
    # Join new room
    join_room(room)
    chat_rooms[room]['users'].add(username)
    connected_users[user_id]['current_room'] = room
    
    # Send room info to user
    emit('joined_room', {
        'room': room,
        'room_name': chat_rooms[room]['name'],
        'messages': chat_rooms[room]['messages'][-50:],  # Last 50 messages
        'users': list(chat_rooms[room]['users'])
    })
    
    # Notify room about new user
    socketio.emit('user_joined', {
        'username': username,
        'room': room,
        'user_count': len(chat_rooms[room]['users'])
    }, room=room)

@socketio.on('send_message')
def handle_send_message(data):
    user_id = session.get('user_id')
    
    if user_id not in connected_users:
        emit('error', {'message': 'User not found'})
        return
    
    user_data = connected_users[user_id]
    username = user_data['username']
    current_room = user_data['current_room']
    
    if not username or not current_room:
        emit('error', {'message': 'Please join a room first'})
        return
    
    message_text = data['message'].strip()
    if not message_text:
        return
    
    message = {
        'id': str(uuid.uuid4()),
        'username': username,
        'message': message_text,
        'timestamp': datetime.now().strftime('%H:%M:%S'),
        'date': datetime.now().strftime('%Y-%m-%d')
    }
    
    # Store message
    chat_rooms[current_room]['messages'].append(message)
    
    # Keep only last 100 messages per room
    if len(chat_rooms[current_room]['messages']) > 100:
        chat_rooms[current_room]['messages'] = chat_rooms[current_room]['messages'][-100:]
    
    # Broadcast message to room
    socketio.emit('new_message', message, room=current_room)

@socketio.on('get_rooms')
def handle_get_rooms():
    rooms_info = {}
    for room_id, room_data in chat_rooms.items():
        rooms_info[room_id] = {
            'name': room_data['name'],
            'user_count': len(room_data['users']),
            'message_count': len(room_data['messages'])
        }
    emit('rooms_list', rooms_info)

@socketio.on('typing')
def handle_typing(data):
    user_id = session.get('user_id')
    if user_id in connected_users:
        user_data = connected_users[user_id]
        if user_data['current_room'] and user_data['username']:
            socketio.emit('user_typing', {
                'username': user_data['username'],
                'typing': data['typing']
            }, room=user_data['current_room'], include_self=False)

if __name__ == '__main__':
    socketio.run(app, debug=True, host='0.0.0.0', port=5000)