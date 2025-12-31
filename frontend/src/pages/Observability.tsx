import { useEffect, useState } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '../components/ui/card';
import { Terminal, FileText, Activity, Server } from 'lucide-react';
import api from '../services/api';
import { useWebSocket } from '../context/WebSocketContext';

const Observability = () => {
    const [logs, setLogs] = useState<any[]>([]);
    const [sessions, setSessions] = useState<any[]>([]);
    const [liveSessions, setLiveSessions] = useState<any[]>([]);
    const [activeTab, setActiveTab] = useState<'logs' | 'sessions' | 'live'>('logs');
    const { lastMessage, isConnected } = useWebSocket();

    useEffect(() => {
        const fetchData = async () => {
            try {
                const logsRes = await api.get('/observability/logs?honeypot_id=shellm-01');
                setLogs(logsRes.data);

                const sessionsRes = await api.get('/observability/sessions');
                setSessions(sessionsRes.data);
            } catch (error) {
                console.error(error);
            }
        };
        fetchData();
    }, []);

    useEffect(() => {
        if (lastMessage) {
            if (lastMessage.type === 'system_log') {
                setLogs(prev => [lastMessage.payload, ...prev].slice(0, 500));
            } else if (lastMessage.type === 'session_start') {
                setLiveSessions(prev => [...prev, { ...lastMessage.payload, commands: [] }]);
            } else if (lastMessage.type === 'session_update') {
                setLiveSessions(prev => {
                    const exists = prev.find(s => s.session_id === lastMessage.payload.session_id);
                    if (exists) {
                        return prev.map(s =>
                            s.session_id === lastMessage.payload.session_id
                                ? { ...s, commands: [...(s.commands || []), lastMessage.payload.command] }
                                : s
                        );
                    } else {
                        // Create new session entry if it doesn't exist (e.g. dashboard opened mid-session)
                        return [...prev, {
                            session_id: lastMessage.payload.session_id,
                            attacker_ip: lastMessage.payload.attacker_ip || 'Unknown',
                            start_time: new Date().toISOString(), // Approximate start time
                            commands: [lastMessage.payload.command]
                        }];
                    }
                });
            } else if (lastMessage.type === 'session_end') {
                setLiveSessions(prev => prev.filter(s => s.session_id !== lastMessage.payload.session_id));
                // Refresh sessions list to show the completed one
                api.get('/observability/sessions').then(res => setSessions(res.data));
            }
        }
    }, [lastMessage]);

    return (
        <div className="space-y-6">
            <div className="flex justify-between items-center">
                <h2 className="text-3xl font-bold tracking-tight">Observability & Forensics</h2>
                <div className="flex items-center gap-2 px-4 py-2 bg-muted rounded-full">
                    <Server className={`h-4 w-4 ${isConnected ? 'text-green-500' : 'text-red-500'}`} />
                    <span className="text-sm font-medium">
                        sheLLM: {isConnected ? 'Active' : 'Disconnected'}
                    </span>
                </div>
            </div>

            <div className="flex space-x-2 border-b">
                <button
                    className={`px-4 py-2 text-sm font-medium border-b-2 transition-colors ${activeTab === 'logs' ? 'border-primary text-primary' : 'border-transparent text-muted-foreground hover:text-foreground'}`}
                    onClick={() => setActiveTab('logs')}
                >
                    System Logs
                </button>
                <button
                    className={`px-4 py-2 text-sm font-medium border-b-2 transition-colors ${activeTab === 'live' ? 'border-primary text-primary' : 'border-transparent text-muted-foreground hover:text-foreground'}`}
                    onClick={() => setActiveTab('live')}
                >
                    Live Sessions ({liveSessions.length})
                </button>
                <button
                    className={`px-4 py-2 text-sm font-medium border-b-2 transition-colors ${activeTab === 'sessions' ? 'border-primary text-primary' : 'border-transparent text-muted-foreground hover:text-foreground'}`}
                    onClick={() => setActiveTab('sessions')}
                >
                    Recorded Sessions
                </button>
            </div>

            {activeTab === 'logs' && (
                <Card>
                    <CardHeader>
                        <CardTitle className="flex items-center gap-2">
                            <FileText className="h-5 w-5" />
                            System Logs
                        </CardTitle>
                    </CardHeader>
                    <CardContent>
                        <div className="rounded-md bg-muted p-4 font-mono text-xs overflow-auto h-[500px]">
                            {logs.map((log, i) => (
                                <div key={i} className="mb-1 border-b border-gray-700/50 pb-1 last:border-0">
                                    <span className="text-muted-foreground">[{new Date(log.timestamp).toLocaleTimeString()}]</span>{' '}
                                    <span className={`${log.level === 'ERROR' ? 'text-red-500' :
                                        log.level === 'WARNING' ? 'text-yellow-500' : 'text-green-500'
                                        } font-bold`}>
                                        [{log.level}]
                                    </span>{' '}
                                    <span className="text-blue-400">[{log.source}]</span>{' '}
                                    {log.message}
                                </div>
                            ))}
                        </div>
                    </CardContent>
                </Card>
            )}

            {activeTab === 'live' && (
                <div className="grid gap-4">
                    {liveSessions.length === 0 ? (
                        <div className="text-center py-12 border rounded-lg bg-muted/10">
                            <Activity className="h-12 w-12 text-muted-foreground mx-auto mb-4" />
                            <h3 className="text-lg font-medium">No Active Sessions</h3>
                            <p className="text-muted-foreground">Waiting for attackers to connect...</p>
                        </div>
                    ) : (
                        liveSessions.map((session, i) => (
                            <Card key={i} className="border-green-500/50">
                                <CardHeader>
                                    <CardTitle className="text-sm font-medium flex justify-between items-center">
                                        <div className="flex items-center gap-2">
                                            <span className="relative flex h-3 w-3">
                                                <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-green-400 opacity-75"></span>
                                                <span className="relative inline-flex rounded-full h-3 w-3 bg-green-500"></span>
                                            </span>
                                            <span>Session {session.session_id.substring(0, 8)}...</span>
                                        </div>
                                        <span className="text-muted-foreground">Attacker: {session.attacker_ip}</span>
                                    </CardTitle>
                                </CardHeader>
                                <CardContent>
                                    <div className="mb-2 text-sm text-muted-foreground">Started at: {new Date(session.start_time).toLocaleString()}</div>
                                    <div className="rounded-md bg-black p-4 font-mono text-xs text-green-400 max-h-[300px] overflow-auto">
                                        {(session.commands || []).map((cmd: any, j: number) => (
                                            <div key={j} className="mb-2">
                                                <div className="flex gap-2">
                                                    <span className="text-blue-500">attacker@honeypot:~$</span>
                                                    <span>{cmd.input}</span>
                                                </div>
                                                <div className="text-gray-400 whitespace-pre-wrap">{cmd.output}</div>
                                            </div>
                                        ))}
                                        {/* Typing indicator */}
                                        <div className="animate-pulse">_</div>
                                    </div>
                                </CardContent>
                            </Card>
                        ))
                    )}
                </div>
            )}

            {activeTab === 'sessions' && (
                <div className="grid gap-4">
                    {sessions.length === 0 ? (
                        <div className="text-center py-8 text-muted-foreground">No sessions recorded.</div>
                    ) : (
                        sessions.map((session, i) => (
                            <Card key={i}>
                                <CardHeader>
                                    <CardTitle className="text-sm font-medium flex justify-between">
                                        <span>Session {session.session_id.substring(0, 8)}...</span>
                                        <span className="text-muted-foreground">{new Date(session.start_time).toLocaleString()}</span>
                                    </CardTitle>
                                </CardHeader>
                                <CardContent>
                                    <div className="rounded-md bg-black p-4 font-mono text-xs text-green-400 max-h-[300px] overflow-auto">
                                        {session.commands.map((cmd: any, j: number) => (
                                            <div key={j} className="mb-2">
                                                <div className="flex gap-2">
                                                    <span className="text-blue-500">attacker@honeypot:~$</span>
                                                    <span>{cmd.input}</span>
                                                </div>
                                                <div className="text-gray-400 whitespace-pre-wrap">{cmd.output}</div>
                                            </div>
                                        ))}
                                    </div>
                                </CardContent>
                            </Card>
                        ))
                    )}
                </div>
            )}
        </div>
    );
};

export default Observability;
