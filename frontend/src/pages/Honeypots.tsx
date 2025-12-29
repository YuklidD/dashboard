import { useEffect, useState } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '../components/ui/card';
import { Button } from '../components/ui/button';
import { Plus, Trash2, RefreshCw } from 'lucide-react';
import api from '../services/api';

interface Honeypot {
    id: string;
    name: string;
    image: string;
    status: string;
    ip_address: string;
    created_at: string;
}

const Honeypots = () => {
    const [honeypots, setHoneypots] = useState<Honeypot[]>([]);
    const [loading, setLoading] = useState(false);

    const fetchHoneypots = async () => {
        setLoading(true);
        try {
            const res = await api.get('/honeypots');
            setHoneypots(res.data);
        } catch (error) {
            console.error(error);
        } finally {
            setLoading(false);
        }
    };

    useEffect(() => {
        fetchHoneypots();
    }, []);

    const handleDeploy = async () => {
        try {
            await api.post('/honeypots', {
                name: `honeypot-${Math.floor(Math.random() * 1000)}`,
                image: 'shellm-honeypot:latest'
            });
            fetchHoneypots();
        } catch (error) {
            console.error(error);
        }
    };

    const handleTerminate = async (id: string) => {
        if (!confirm('Are you sure you want to terminate this honeypot?')) return;
        try {
            await api.delete(`/honeypots/${id}`);
            fetchHoneypots();
        } catch (error) {
            console.error(error);
        }
    };

    return (
        <div className="space-y-6">
            <div className="flex items-center justify-between">
                <h2 className="text-3xl font-bold tracking-tight">Honeypot Management</h2>
                <Button onClick={handleDeploy}>
                    <Plus className="mr-2 h-4 w-4" /> Deploy Honeypot
                </Button>
            </div>

            <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
                {honeypots.map((hp) => (
                    <Card key={hp.id}>
                        <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                            <CardTitle className="text-sm font-medium">{hp.name}</CardTitle>
                            <div className={`px-2 py-1 rounded-full text-xs font-semibold ${hp.status === 'Running' ? 'bg-green-500/10 text-green-500' :
                                    hp.status === 'Pending' ? 'bg-yellow-500/10 text-yellow-500' :
                                        'bg-red-500/10 text-red-500'
                                }`}>
                                {hp.status}
                            </div>
                        </CardHeader>
                        <CardContent>
                            <div className="mt-4 space-y-2">
                                <div className="flex justify-between text-sm">
                                    <span className="text-muted-foreground">ID:</span>
                                    <span className="font-mono">{hp.id.substring(0, 8)}...</span>
                                </div>
                                <div className="flex justify-between text-sm">
                                    <span className="text-muted-foreground">IP:</span>
                                    <span className="font-mono">{hp.ip_address || 'Pending'}</span>
                                </div>
                                <div className="flex justify-between text-sm">
                                    <span className="text-muted-foreground">Image:</span>
                                    <span>{hp.image}</span>
                                </div>
                            </div>
                            <div className="mt-6 flex justify-end">
                                <Button variant="destructive" size="sm" onClick={() => handleTerminate(hp.id)}>
                                    <Trash2 className="h-4 w-4" />
                                </Button>
                            </div>
                        </CardContent>
                    </Card>
                ))}

                {honeypots.length === 0 && !loading && (
                    <div className="col-span-full text-center py-12 text-muted-foreground">
                        No honeypots deployed. Click "Deploy Honeypot" to start.
                    </div>
                )}
            </div>
        </div>
    );
};

export default Honeypots;
