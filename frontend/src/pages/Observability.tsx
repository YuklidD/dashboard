import { useEffect, useState } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '../components/ui/card';
import { FileText } from 'lucide-react';
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

            <div className="flex justify-between items-end border-b pb-2">
                <div className="flex space-x-2">
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
                <div className="flex gap-2">
                    <button
                        onClick={() => window.open('http://localhost:8000/api/v1/ioc/export?format=json', '_blank')}
                        className="text-xs bg-secondary text-secondary-foreground hover:bg-secondary/80 px-3 py-1.5 rounded-md flex items-center gap-1"
                    >
                        Export JSON
                    </button>
                    <button
                        onClick={() => window.open('http://localhost:8000/api/v1/ioc/export?format=csv', '_blank')}
                        className="text-xs bg-primary text-primary-foreground hover:bg-primary/90 px-3 py-1.5 rounded-md flex items-center gap-1"
                    >
                        Export CSV
                    </button>
                </div>
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
                                    <CardTitle className="text-sm font-medium flex flex-col gap-2">
                                        <div className="flex justify-between items-center">
                                            <span className="flex items-center gap-2">
                                                Session {session.session_id}
                                                {session.country && (
                                                    <span className="text-xs px-2 py-0.5 rounded-full bg-blue-100 text-blue-700 dark:bg-blue-900 dark:text-blue-100">
                                                        {session.country}
                                                    </span>
                                                )}
                                            </span>
                                            <span className="text-muted-foreground">{session.start_time}</span>
                                        </div>
                                        {session.mitre_techniques && (
                                            <div className="flex flex-wrap gap-2 mt-1">
                                                {JSON.parse(session.mitre_techniques).map((tech: any, t: number) => (
                                                    <span key={t} className="text-xs border border-red-200 bg-red-50 text-red-700 px-2 py-0.5 rounded dark:bg-red-900/20 dark:border-red-800 dark:text-red-400">
                                                        {tech.id}: {tech.name}
                                                    </span>
                                                ))}
                                            </div>
                                        )}
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
