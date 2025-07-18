from flask import Flask, request, session
from flask_socketio import SocketIO, emit, join_room, leave_room, rooms
from flask_cors import CORS
import uuid
from datetime import datetime
import json
import os

app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'your-secret-key-here')

# Enable CORS for all routes
CORS(app)

# Configure SocketIO with CORS
socketio = SocketIO(app, cors_allowed_origins="*", logger=True, engineio_logger=True)

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
def health_check():
    """Health check endpoint"""
    return {
        'status': 'healthy',
        'service': 'Chat Backend',
        'timestamp': datetime.now().isoformat()
    }

@app.route('/api/rooms')
def get_rooms_api():
    """REST API endpoint to get room information"""
    rooms_info = {}
    for room_id, room_data in chat_rooms.items():
        rooms_info[room_id] = {
            'name': room_data['name'],
            'user_count': len(room_data['users']),
            'message_count': len(room_data['messages'])
        }
    return rooms_info

@app.route('/api/rooms/<room_id>/messages')
def get_room_messages(room_id):
    """REST API endpoint to get messages for a specific room"""
    if room_id not in chat_rooms:
        return {'error': 'Room not found'}, 404
    
    limit = request.args.get('limit', 50, type=int)
    messages = chat_rooms[room_id]['messages'][-limit:]
    return {'messages': messages}

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
    port = int(os.environ.get('PORT', 5000))
    debug = os.environ.get('DEBUG', 'True').lower() == 'true'
    socketio.run(app, debug=debug, host='0.0.0.0', port=port)