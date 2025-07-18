const CONFIG = {
    // Backend server URL
    SERVER_URL: 'http://localhost:5000',
    
    // Socket.IO options
    SOCKET_OPTIONS: {
        autoConnect: true,
        reconnection: true,
        reconnectionAttempts: 5,
        // ... more options
    },
    
    // Application settings
    APP_SETTINGS: {
        MAX_MESSAGE_LENGTH: 500,
        TYPING_TIMEOUT: 1000,
        // ... more settings
    },
    
    // UI settings
    UI_SETTINGS: {
        SHOW_CONNECTION_STATUS: true,
        SHOW_TYPING_INDICATOR: true,
        // ... more UI options
    }
};