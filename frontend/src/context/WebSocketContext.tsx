import React, { createContext, useContext, useEffect, useRef, useState } from 'react';

interface WebSocketContextType {
    isConnected: boolean;
    lastMessage: any;
}

const WebSocketContext = createContext<WebSocketContextType | null>(null);

export const WebSocketProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
    const [isConnected, setIsConnected] = useState(false);
    const [lastMessage, setLastMessage] = useState<any>(null);
    const ws = useRef<WebSocket | null>(null);

    useEffect(() => {
        const connect = () => {
            const wsUrl = import.meta.env.VITE_WS_URL || 'ws://localhost:8000/api/v1/ws/events';
            ws.current = new WebSocket(wsUrl);

            ws.current.onopen = () => {
                console.log('WebSocket Connected');
                setIsConnected(true);
            };

            ws.current.onclose = () => {
                console.log('WebSocket Disconnected');
                setIsConnected(false);
                // Reconnect after 3s
                setTimeout(connect, 3000);
            };

            ws.current.onmessage = (event) => {
                try {
                    const data = JSON.parse(event.data);
                    setLastMessage(data);
                } catch (e) {
                    console.error('Failed to parse WS message', e);
                }
            };
        };

        connect();

        return () => {
            ws.current?.close();
        };
    }, []);

    return (
        <WebSocketContext.Provider value={{ isConnected, lastMessage }}>
            {children}
        </WebSocketContext.Provider>
    );
};

export const useWebSocket = () => {
    const context = useContext(WebSocketContext);
    if (!context) throw new Error('useWebSocket must be used within a WebSocketProvider');
    return context;
};
