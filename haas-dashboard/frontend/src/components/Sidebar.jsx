import React from 'react';
import { Link, useLocation } from 'react-router-dom';
import { LayoutDashboard, Shield, Activity, Terminal, Settings } from 'lucide-react';

const Sidebar = () => {
    const location = useLocation();

    const navItems = [
        { path: '/', label: 'Dashboard', icon: LayoutDashboard },
        { path: '/waf', label: 'WAF Control', icon: Shield },
        { path: '/honeypots', label: 'Honeypots', icon: Terminal },
        { path: '/metrics', label: 'Metrics', icon: Activity },
        { path: '/settings', label: 'Settings', icon: Settings },
    ];

    return (
        <div className="sidebar" style={{
            width: '250px',
            height: '100vh',
            backgroundColor: 'var(--bg-secondary)',
            padding: '20px',
            display: 'flex',
            flexDirection: 'column',
            borderRight: '1px solid #334155'
        }}>
            <h2 style={{ color: 'var(--accent)', marginBottom: '40px' }}>HaaS Central</h2>
            <nav style={{ display: 'flex', flexDirection: 'column', gap: '10px' }}>
                {navItems.map((item) => {
                    const Icon = item.icon;
                    const isActive = location.pathname === item.path;
                    return (
                        <Link
                            key={item.path}
                            to={item.path}
                            style={{
                                display: 'flex',
                                alignItems: 'center',
                                gap: '12px',
                                padding: '12px',
                                borderRadius: '8px',
                                backgroundColor: isActive ? 'rgba(59, 130, 246, 0.1)' : 'transparent',
                                color: isActive ? 'var(--accent)' : 'var(--text-secondary)',
                                transition: 'all 0.2s'
                            }}
                        >
                            <Icon size={20} />
                            <span>{item.label}</span>
                        </Link>
                    );
                })}
            </nav>
        </div>
    );
};

export default Sidebar;
