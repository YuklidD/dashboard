import React from 'react';
import { removeToken } from '../utils/auth';
import { useNavigate } from 'react-router-dom';
import { LogOut } from 'lucide-react';

const Header = () => {
    const navigate = useNavigate();

    const handleLogout = () => {
        removeToken();
        navigate('/login');
    };

    return (
        <header style={{
            height: '64px',
            backgroundColor: 'var(--bg-secondary)',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'flex-end',
            padding: '0 32px',
            borderBottom: '1px solid #334155'
        }}>
            <button
                onClick={handleLogout}
                style={{
                    display: 'flex',
                    alignItems: 'center',
                    gap: '8px',
                    background: 'transparent',
                    color: 'var(--text-secondary)',
                    fontSize: '14px'
                }}
            >
                <LogOut size={18} />
                Logout
            </button>
        </header>
    );
};

export default Header;
