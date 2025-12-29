import React, { useEffect, useState } from 'react';
import { getHoneypots, getMetrics } from '../services/api';
import { BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer } from 'recharts';

const Dashboard = () => {
    const [honeypots, setHoneypots] = useState([]);
    const [metrics, setMetrics] = useState([]);

    useEffect(() => {
        const fetchData = async () => {
            try {
                const hpData = await getHoneypots();
                setHoneypots(hpData);
                // Mock metrics for now as backend might not have data
                setMetrics([
                    { name: 'SSH', attacks: 400 },
                    { name: 'HTTP', attacks: 300 },
                    { name: 'FTP', attacks: 200 },
                    { name: 'Telnet', attacks: 100 },
                ]);
            } catch (error) {
                console.error("Error fetching data", error);
            }
        };
        fetchData();
    }, []);

    return (
        <div>
            <h1 style={{ fontSize: '24px', fontWeight: 'bold', marginBottom: '32px' }}>System Overview</h1>

            <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(300px, 1fr))', gap: '24px', marginBottom: '32px' }}>
                <div style={{ backgroundColor: 'var(--bg-secondary)', padding: '24px', borderRadius: '12px' }}>
                    <h3 style={{ color: 'var(--text-secondary)', marginBottom: '16px' }}>Active Honeypots</h3>
                    <div style={{ fontSize: '36px', fontWeight: 'bold', color: 'var(--accent)' }}>{honeypots.length}</div>
                </div>
                <div style={{ backgroundColor: 'var(--bg-secondary)', padding: '24px', borderRadius: '12px' }}>
                    <h3 style={{ color: 'var(--text-secondary)', marginBottom: '16px' }}>Total Attacks (24h)</h3>
                    <div style={{ fontSize: '36px', fontWeight: 'bold', color: 'var(--danger)' }}>1,234</div>
                </div>
                <div style={{ backgroundColor: 'var(--bg-secondary)', padding: '24px', borderRadius: '12px' }}>
                    <h3 style={{ color: 'var(--text-secondary)', marginBottom: '16px' }}>WAF Blocks</h3>
                    <div style={{ fontSize: '36px', fontWeight: 'bold', color: 'var(--warning)' }}>89</div>
                </div>
            </div>

            <div style={{ backgroundColor: 'var(--bg-secondary)', padding: '24px', borderRadius: '12px', height: '400px' }}>
                <h3 style={{ marginBottom: '24px' }}>Attack Distribution</h3>
                <ResponsiveContainer width="100%" height="100%">
                    <BarChart data={metrics}>
                        <XAxis dataKey="name" stroke="var(--text-secondary)" />
                        <YAxis stroke="var(--text-secondary)" />
                        <Tooltip
                            contentStyle={{ backgroundColor: 'var(--bg-primary)', border: 'none' }}
                            itemStyle={{ color: 'var(--text-primary)' }}
                        />
                        <Bar dataKey="attacks" fill="var(--accent)" radius={[4, 4, 0, 0]} />
                    </BarChart>
                </ResponsiveContainer>
            </div>
        </div>
    );
};

export default Dashboard;
