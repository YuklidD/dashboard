import { useState, useEffect } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '../components/ui/card';
import { cveService, CVEItem } from '../services/cveService';
import { Calendar, ExternalLink, Activity } from 'lucide-react';

const CVEs = () => {
    const [cves, setCves] = useState<CVEItem[]>([]);
    const [loading, setLoading] = useState(true);
    const [days, setDays] = useState(7);
    const [limit, setLimit] = useState(20);

    useEffect(() => {
        const fetchCVEs = async () => {
            setLoading(true);
            try {
                const data = await cveService.getRecentCVEs(days, limit);
                setCves(data.cves);
            } catch (error) {
                console.error("Failed to fetch CVEs", error);
            } finally {
                setLoading(false);
            }
        };
        fetchCVEs();
    }, [days, limit]);

    const getSeverityColor = (severity?: string) => {
        if (!severity) return 'text-gray-500 bg-gray-100';
        switch (severity.toUpperCase()) {
            case 'CRITICAL': return 'text-red-700 bg-red-100 ring-red-600/20';
            case 'HIGH': return 'text-orange-700 bg-orange-100 ring-orange-600/20';
            case 'MEDIUM': return 'text-yellow-700 bg-yellow-100 ring-yellow-600/20';
            case 'LOW': return 'text-green-700 bg-green-100 ring-green-600/20';
            default: return 'text-gray-500 bg-gray-100';
        }
    };

    return (
        <div className="space-y-6">
            <div className="flex items-center justify-between">
                <h2 className="text-3xl font-bold tracking-tight">Recent Vulnerabilities (CVEs)</h2>
                <div className="flex gap-4">
                    <select
                        className="rounded-md border border-input bg-background px-3 py-1 text-sm shadow-sm transition-colors focus-visible:outline-none focus-visible:ring-1 focus-visible:ring-ring"
                        value={days}
                        onChange={(e) => setDays(Number(e.target.value))}
                    >
                        <option value={3}>Last 3 Days</option>
                        <option value={7}>Last 7 Days</option>
                        <option value={30}>Last 30 Days</option>
                    </select>
                    <select
                        className="rounded-md border border-input bg-background px-3 py-1 text-sm shadow-sm transition-colors focus-visible:outline-none focus-visible:ring-1 focus-visible:ring-ring"
                        value={limit}
                        onChange={(e) => setLimit(Number(e.target.value))}
                    >
                        <option value={10}>10 Results</option>
                        <option value={20}>20 Results</option>
                        <option value={50}>50 Results</option>
                    </select>
                </div>
            </div>

            {loading ? (
                <div className="text-center py-10 text-muted-foreground">Loading recent CVEs...</div>
            ) : (
                <div className="grid gap-4">
                    {cves.map((cve) => (
                        <Card key={cve.id} className="hover:shadow-md transition-shadow">
                            <CardHeader className="pb-2">
                                <div className="flex items-start justify-between">
                                    <div className="space-y-1">
                                        <CardTitle className="text-lg font-semibold flex items-center gap-2">
                                            {cve.id}
                                            <a
                                                href={`https://www.cve.org/CVERecord?id=${cve.id}`}
                                                target="_blank"
                                                rel="noreferrer"
                                                className="text-muted-foreground hover:text-primary"
                                            >
                                                <ExternalLink className="h-4 w-4" />
                                            </a>
                                        </CardTitle>
                                        <div className="flex items-center gap-2 text-sm text-muted-foreground">
                                            <Calendar className="h-3 w-3" />
                                            <span>{new Date(cve.published).toISOString().split('T')[0]}</span>
                                            <span className="text-xs px-2 py-0.5 rounded-full bg-secondary text-secondary-foreground">
                                                {cve.vulnStatus}
                                            </span>
                                        </div>
                                    </div>
                                    {cve.metrics && (
                                        <div className={`flex items-center gap-1.5 px-3 py-1 rounded-full text-xs font-medium ring-1 ring-inset ${getSeverityColor(cve.metrics.severity)}`}>
                                            <Activity className="h-3 w-3" />
                                            {cve.metrics.baseScore} {cve.metrics.severity}
                                        </div>
                                    )}
                                </div>
                            </CardHeader>
                            <CardContent>
                                <p className="text-sm text-muted-foreground leading-relaxed">
                                    {cve.description}
                                </p>
                            </CardContent>
                        </Card>
                    ))}
                </div>
            )}
        </div>
    );
};

export default CVEs;
