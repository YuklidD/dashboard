import { useEffect, useState } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '../components/ui/card';
import { useWebSocket } from '../context/WebSocketContext';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from 'recharts';
import { ShieldAlert, Activity, Server, Users } from 'lucide-react';
import api from '../services/api';

const Dashboard = () => {
    const { lastMessage } = useWebSocket();
    const [stats, setStats] = useState({
        activeHoneypots: 0,
        totalAttacks: 0,
        activeSessions: 0
    });
    const [alerts, setAlerts] = useState<any[]>([]);
    const [chartData, setChartData] = useState<any[]>([]);

    useEffect(() => {
        // Fetch initial stats
        const fetchStats = async () => {
            try {
                const honeypots = await api.get('/honeypots');
                setStats(prev => ({ ...prev, activeHoneypots: honeypots.data.length }));
                // Mock other stats for now or fetch from metrics endpoint
            } catch (error) {
                console.error("Failed to fetch stats", error);
            }
        };
        fetchStats();

        // Generate mock chart data
        const data = Array.from({ length: 20 }, (_, i) => ({
            time: `${i}:00`,
            attacks: Math.floor(Math.random() * 50) + 10
        }));
        setChartData(data);
    }, []);

    useEffect(() => {
        if (lastMessage) {
            if (lastMessage.type === 'waf_bypass') {
                setAlerts(prev => [lastMessage.payload, ...prev].slice(0, 5));
                setStats(prev => ({ ...prev, totalAttacks: prev.totalAttacks + 1 }));
            }
        }
    }, [lastMessage]);

    return (
        <div className="space-y-6">
            <h2 className="text-3xl font-bold tracking-tight">Dashboard Overview</h2>

            <div className="grid gap-4 md:grid-cols-3">
                <Card>
                    <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                        <CardTitle className="text-sm font-medium">Active Honeypots</CardTitle>
                        <Server className="h-4 w-4 text-muted-foreground" />
                    </CardHeader>
                    <CardContent>
                        <div className="text-2xl font-bold">{stats.activeHoneypots}</div>
                    </CardContent>
                </Card>
                <Card>
                    <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                        <CardTitle className="text-sm font-medium">Total Attacks</CardTitle>
                        <ShieldAlert className="h-4 w-4 text-muted-foreground" />
                    </CardHeader>
                    <CardContent>
                        <div className="text-2xl font-bold">{stats.totalAttacks}</div>
                    </CardContent>
                </Card>
                <Card>
                    <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                        <CardTitle className="text-sm font-medium">Active Sessions</CardTitle>
                        <Users className="h-4 w-4 text-muted-foreground" />
                    </CardHeader>
                    <CardContent>
                        <div className="text-2xl font-bold">{stats.activeSessions}</div>
                    </CardContent>
                </Card>
            </div>

            <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-7">
                <Card className="col-span-4">
                    <CardHeader>
                        <CardTitle>Attack Traffic</CardTitle>
                    </CardHeader>
                    <CardContent className="pl-2">
                        <div className="h-[300px]">
                            <ResponsiveContainer width="100%" height="100%">
                                <LineChart data={chartData}>
                                    <CartesianGrid strokeDasharray="3 3" className="stroke-muted" />
                                    <XAxis dataKey="time" className="text-xs" />
                                    <YAxis className="text-xs" />
                                    <Tooltip
                                        contentStyle={{ backgroundColor: 'hsl(var(--card))', borderColor: 'hsl(var(--border))' }}
                                        itemStyle={{ color: 'hsl(var(--foreground))' }}
                                    />
                                    <Line type="monotone" dataKey="attacks" stroke="hsl(var(--primary))" strokeWidth={2} dot={false} />
                                </LineChart>
                            </ResponsiveContainer>
                        </div>
                    </CardContent>
                </Card>

                <Card className="col-span-3">
                    <CardHeader>
                        <CardTitle className="flex items-center gap-2">
                            <Activity className="h-5 w-5 text-destructive" />
                            WAF Bypass Alerts
                        </CardTitle>
                    </CardHeader>
                    <CardContent>
                        <div className="space-y-4">
                            {alerts.length === 0 ? (
                                <p className="text-sm text-muted-foreground">No recent alerts.</p>
                            ) : (
                                alerts.map((alert, i) => (
                                    <div key={i} className="flex items-start gap-4 rounded-md border p-3 bg-destructive/10">
                                        <ShieldAlert className="h-5 w-5 text-destructive mt-0.5" />
                                        <div className="space-y-1">
                                            <p className="text-sm font-medium leading-none text-destructive">
                                                WAF Bypass Detected
                                            </p>
                                            <p className="text-xs text-muted-foreground">
                                                Source: {alert.source_ip || 'Unknown'}
                                            </p>
                                            <p className="text-xs text-muted-foreground">
                                                Payload: {alert.payload || 'N/A'}
                                            </p>
                                        </div>
                                    </div>
                                ))
                            )}
                        </div>
                    </CardContent>
                </Card>
            </div>
        </div>
    );
};

export default Dashboard;
