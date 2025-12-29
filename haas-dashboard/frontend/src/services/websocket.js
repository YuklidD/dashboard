class WebSocketService {
    constructor() {
        this.socket = null;
        this.listeners = [];
    }

    connect() {
        const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
        const host = window.location.host; // In dev this might be localhost:5173, but proxy handles /ws to localhost:8000
        // If using vite proxy, we connect to /ws on the same host
        this.socket = new WebSocket(`${protocol}//${host}/ws`);

        this.socket.onopen = () => {
            console.log('WebSocket Connected');
        };

        this.socket.onmessage = (event) => {
            const data = JSON.parse(event.data);
            this.listeners.forEach(listener => listener(data));
        };

        this.socket.onclose = () => {
            console.log('WebSocket Disconnected');
            // Reconnect logic could go here
        };
    }

    subscribe(listener) {
        this.listeners.push(listener);
        return () => {
            this.listeners = this.listeners.filter(l => l !== listener);
        };
    }

    send(message) {
        if (this.socket && this.socket.readyState === WebSocket.OPEN) {
            this.socket.send(JSON.stringify(message));
        }
    }
}

export const wsService = new WebSocketService();
