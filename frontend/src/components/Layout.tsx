import { Link, Outlet, useLocation } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import { useWebSocket } from '../context/WebSocketContext';
import { LayoutDashboard, Shield, Activity, LogOut, Server } from 'lucide-react';
import { cn } from './ui/button';

const Layout = () => {
    const { logout, user } = useAuth();
    const { isConnected } = useWebSocket();
    const location = useLocation();

    const navItems = [
        { href: '/dashboard', label: 'Overview', icon: LayoutDashboard },
        { href: '/honeypots', label: 'Honeypots', icon: Server },
        { href: '/observability', label: 'Observability', icon: Activity },
    ];

    return (
        <div className="flex h-screen bg-background text-foreground">
            {/* Sidebar */}
            <aside className="w-64 border-r bg-card hidden md:flex flex-col">
                <div className="p-6 border-b">
                    <h1 className="text-xl font-bold flex items-center gap-2">
                        <Shield className="h-6 w-6 text-primary" />
                        HaaS Platform
                    </h1>
                    <div className="mt-2 flex items-center gap-2 text-xs text-muted-foreground">
                        <span className={cn("h-2 w-2 rounded-full", isConnected ? "bg-green-500" : "bg-red-500")} />
                        {isConnected ? "System Online" : "Disconnected"}
                    </div>
                </div>

                <nav className="flex-1 p-4 space-y-2">
                    {navItems.map((item) => {
                        const Icon = item.icon;
                        const isActive = location.pathname === item.href;
                        return (
                            <Link
                                key={item.href}
                                to={item.href}
                                className={cn(
                                    "flex items-center gap-3 px-3 py-2 rounded-md text-sm font-medium transition-colors",
                                    isActive
                                        ? "bg-primary text-primary-foreground"
                                        : "hover:bg-accent hover:text-accent-foreground"
                                )}
                            >
                                <Icon className="h-4 w-4" />
                                {item.label}
                            </Link>
                        );
                    })}
                </nav>

                <div className="p-4 border-t">
                    <div className="flex items-center gap-3 px-3 py-2">
                        <div className="flex-1">
                            <p className="text-sm font-medium">{user?.username}</p>
                            <p className="text-xs text-muted-foreground capitalize">{user?.role}</p>
                        </div>
                        <button onClick={logout} className="text-muted-foreground hover:text-foreground">
                            <LogOut className="h-4 w-4" />
                        </button>
                    </div>
                </div>
            </aside>

            {/* Main Content */}
            <main className="flex-1 overflow-auto">
                <div className="p-8">
                    <Outlet />
                </div>
            </main>
        </div>
    );
};

export default Layout;
