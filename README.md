# chat_application

A simple real-time chat application built using **Flask**, **Socket.IO**, and **HTML/CSS/JavaScript**. This project enables multiple users to join chat rooms and exchange messages instantly — ideal for learning real-time web communication using Python.

## 🚀 Features

- Real-time two-way communication using WebSockets
- Multiple user support with distinct usernames
- Join/create chat rooms dynamically
- Message broadcasting to all users in the same room
- Simple and responsive UI

## 🛠️ Tech Stack

- **Backend**: Flask, Flask-SocketIO
- **Frontend**: HTML, CSS, JavaScript
- **Socket Communication**: WebSockets via Socket.IO

## 📸 Screenshots

> _Add screenshots of your UI here, e.g., chat screen, room creation, etc._

![Chat Screenshot](https://github.com/bharathiprasad/chat_application/tree/main/chat_app/output)

## 🧑‍💻 How to Run Locally

1. **Clone the repository**
   ```bash
   git clone https://github.com/bharathiprasad/chat_application.git
   cd chat_application
   ```

2. **Create a virtual environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Run the Flask application**
   ```bash
   python app.py
   ```

5. **Open in browser**
   Visit `http://localhost:5000` in your browser.

## 📂 Project Structure

```
chat_application/
│
├── static/             # CSS and client-side JS files
│   └── style.css
│
├── templates/          # HTML templates
│   ├── index.html
│   └── chat.html
│
├── app.py              # Main Flask server
├── requirements.txt    # Python dependencies
└── README.md
```

## 🧪 Future Enhancements

- User authentication and session management
- Private messaging support
- Chat history persistence with a database
- Message timestamps
- Improved UI/UX

## 🤝 Contributing

Contributions, issues, and feature requests are welcome!  
Feel free to fork the project and submit a pull request.

---

**Author:** [Bharathi Prasad](https://github.com/bharathiprasad)
