import { useEffect, useState } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '../components/ui/card';
import { Terminal, FileText } from 'lucide-react';
import api from '../services/api';

const Observability = () => {
    const [logs, setLogs] = useState<any[]>([]);
    const [sessions, setSessions] = useState<any[]>([]);
    const [activeTab, setActiveTab] = useState<'logs' | 'sessions'>('logs');

    useEffect(() => {
        const fetchData = async () => {
            try {
                // In a real app, we'd pick a specific honeypot ID
                // For now, we just fetch logs for "any" honeypot to demonstrate
                const logsRes = await api.get('/observability/logs?honeypot_id=demo');
                setLogs(logsRes.data);

                const sessionsRes = await api.get('/observability/sessions');
                setSessions(sessionsRes.data);
            } catch (error) {
                console.error(error);
            }
        };
        fetchData();
    }, []);

    return (
        <div className="space-y-6">
            <h2 className="text-3xl font-bold tracking-tight">Observability & Forensics</h2>

            <div className="flex space-x-2 border-b">
                <button
                    className={`px-4 py-2 text-sm font-medium border-b-2 transition-colors ${activeTab === 'logs' ? 'border-primary text-primary' : 'border-transparent text-muted-foreground hover:text-foreground'
                        }`}
                    onClick={() => setActiveTab('logs')}
                >
                    System Logs
                </button>
                <button
                    className={`px-4 py-2 text-sm font-medium border-b-2 transition-colors ${activeTab === 'sessions' ? 'border-primary text-primary' : 'border-transparent text-muted-foreground hover:text-foreground'
                        }`}
                    onClick={() => setActiveTab('sessions')}
                >
                    sheLLM Sessions
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
                                <div key={i} className="mb-1">
                                    <span className="text-muted-foreground">[{log.timestamp}]</span>{' '}
                                    <span className={`${log.level === 'ERROR' ? 'text-red-500' :
                                            log.level === 'WARNING' ? 'text-yellow-500' : 'text-green-500'
                                        }`}>
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

            {activeTab === 'sessions' && (
                <div className="grid gap-4">
                    {sessions.length === 0 ? (
                        <div className="text-center py-8 text-muted-foreground">No sessions recorded.</div>
                    ) : (
                        sessions.map((session, i) => (
                            <Card key={i}>
                                <CardHeader>
                                    <CardTitle className="text-sm font-medium flex justify-between">
                                        <span>Session {session.session_id}</span>
                                        <span className="text-muted-foreground">{session.start_time}</span>
                                    </CardTitle>
                                </CardHeader>
                                <CardContent>
                                    <div className="rounded-md bg-black p-4 font-mono text-xs text-green-400">
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
