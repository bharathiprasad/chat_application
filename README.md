# Real-Time Chat Application
A simple real-time chat application built using **Flask**, **Socket.IO**, and **HTML/CSS/JavaScript**. This project enables multiple users to join chat rooms and exchange messages instantly — ideal for learning real-time web communication using Python.

## Project Structure

```
chat-app/
├── backend/
│   ├── app.py              # Flask backend application
│   ├── requirements.txt    # Python dependencies
├── frontend/
│   ├── index.html         # Main HTML file
│   ├── styles.css         # Application styles
│   ├── app.js            # Main JavaScript application
│   ├── config.js         # Configuration file
└── README.md             # This file
```
## Quick Start

### 1. Backend Setup

```bash
# Navigate to backend directory
cd backend

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Run the backend server
python app.py
```

The backend will run on `http://localhost:5000`

### 2. Frontend Setup

```bash
# Navigate to frontend directory
cd frontend

# Serve the frontend (using Python)
python -m http.server 8080

# Or using Node.js
npx http-server -p 8080
```

The frontend will be available at `http://localhost:8080`

### 3. Access the Application

Open your browser and go to `http://localhost:8080`

## Features

### Backend Features
- **Real-time WebSocket communication** with Socket.IO
- **Multiple chat rooms** with user presence tracking
- **Message history** with automatic cleanup
- **Typing indicators** for better user experience
- **RESTful API endpoints** for room and message data
- **CORS support** for frontend integration
- **Session management** with unique user IDs
- **Error handling** and validation

### Frontend Features
- **Modern responsive design** that works on all devices
- **Real-time messaging** with WebSocket support
- **Multiple chat rooms** with user counts
- **Typing indicators** and user presence
- **Connection status monitoring** with reconnection
- **Browser notifications** for new messages
- **Message history** with smooth scrolling
- **Input validation** and error handling

## Technology Stack

### Backend
- **Python 3.7+**
- **Flask** - Web framework
- **Flask-SocketIO** - WebSocket support
- **Flask-CORS** - Cross-origin resource sharing
- **Gunicorn** - WSGI HTTP Server (for production)

### Frontend
- **HTML5** - Structure and semantics
- **CSS3** - Modern styling with flexbox and animations
- **Vanilla JavaScript** - No frameworks, pure JS
- **Socket.IO Client** - WebSocket communication
- **Responsive Design** - Mobile-first approach

## Configuration

### Backend Configuration (.env)
```
SECRET_KEY=your-secret-key-here-change-this-in-production
PORT=5000
DEBUG=True
FLASK_ENV=development
```

### Frontend Configuration (config.js)
```javascript
const CONFIG = {
    SERVER_URL: 'http://localhost:5000',
    SOCKET_OPTIONS: {
        autoConnect: true,
        reconnection: true,
        reconnectionAttempts: 5,
        // ... more options
    },
    APP_SETTINGS: {
        MAX_MESSAGE_LENGTH: 500,
        TYPING_TIMEOUT: 1000,
        // ... more settings
    }
};
```

## Development

### Backend Development
```bash
cd backend
python app.py
```

### Frontend Development
```bash
cd frontend
npx http-server -p 8080
```

### Making Changes
1. Backend changes: Restart the Flask server
2. Frontend changes: Refresh the browser

## API Documentation

### WebSocket Events

#### Client to Server
- `set_username` - Set user's username
- `join_room` - Join a chat room
- `send_message` - Send a message
- `typing` - Typing indicator
- `get_rooms` - Get available rooms

#### Server to Client
- `username_set` - Username successfully set
- `rooms_list` - List of available rooms
- `joined_room` - Successfully joined room
- `new_message` - New message received
- `user_joined` - User joined room
- `user_left` - User left room
- `user_typing` - User typing indicator
- `error` - Error message

### REST API Endpoints
- `GET /` - Health check
- `GET /api/rooms` - Get all rooms
- `GET /api/rooms/<room_id>/messages` - Get room messages

## Default Chat Rooms

The application comes with three default rooms:
- **General** - General discussion
- **Tech Talk** - Technology-related discussions
- **Random** - Random conversations

## Security Features

- Input validation and sanitization
- XSS protection with HTML escaping
- CORS configuration
- Session management with UUIDs
- Rate limiting considerations

## Browser Support

- Chrome 60+
- Firefox 55+
- Safari 11+
- Edge 79+

## 🤝 Contributing

Contributions, issues, and feature requests are welcome!  
Feel free to fork the project and submit a pull request.

---

**Author:** [Bharathi Prasad](https://github.com/bharathiprasad)
