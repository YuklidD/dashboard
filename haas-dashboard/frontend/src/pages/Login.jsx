import React, { useState } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import { login, setToken } from '../services/api'; // Fix import path if needed, wait, api.js exports login but setToken is in utils/auth.js. Wait, I exported setToken from api.js? No, I imported it in api.js but didn't export it. I should import setToken from utils/auth.
import { setToken as saveToken } from '../utils/auth';

const Login = () => {
    const [email, setEmail] = useState('');
    const [password, setPassword] = useState('');
    const [error, setError] = useState('');
    const navigate = useNavigate();

    const handleSubmit = async (e) => {
        e.preventDefault();
        try {
            const data = await login(email, password);
            saveToken(data.access_token);
            navigate('/');
        } catch (err) {
            setError('Invalid credentials');
        }
    };

    return (
        <div style={{
            height: '100vh',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            backgroundColor: 'var(--bg-primary)'
        }}>
            <div style={{
                width: '400px',
                padding: '40px',
                backgroundColor: 'var(--bg-secondary)',
                borderRadius: '12px',
                boxShadow: '0 4px 6px -1px rgba(0, 0, 0, 0.1)'
            }}>
                <h1 style={{ textAlign: 'center', marginBottom: '32px', color: 'var(--text-primary)' }}>Login</h1>
                {error && <div style={{ color: 'var(--danger)', marginBottom: '16px', textAlign: 'center' }}>{error}</div>}
                <form onSubmit={handleSubmit} style={{ display: 'flex', flexDirection: 'column', gap: '20px' }}>
                    <input
                        type="email"
                        placeholder="Email"
                        value={email}
                        onChange={(e) => setEmail(e.target.value)}
                        style={{
                            padding: '12px',
                            borderRadius: '8px',
                            border: '1px solid #334155',
                            backgroundColor: 'var(--bg-primary)',
                            color: 'var(--text-primary)'
                        }}
                    />
                    <input
                        type="password"
                        placeholder="Password"
                        value={password}
                        onChange={(e) => setPassword(e.target.value)}
                        style={{
                            padding: '12px',
                            borderRadius: '8px',
                            border: '1px solid #334155',
                            backgroundColor: 'var(--bg-primary)',
                            color: 'var(--text-primary)'
                        }}
                    />
                    <button
                        type="submit"
                        style={{
                            padding: '12px',
                            borderRadius: '8px',
                            backgroundColor: 'var(--accent)',
                            color: 'white',
                            fontWeight: '600',
                            marginTop: '10px'
                        }}
                    >
                        Sign In
                    </button>
                </form>
                <div style={{ marginTop: '20px', textAlign: 'center', color: 'var(--text-secondary)' }}>
                    Don't have an account? <Link to="/register" style={{ color: 'var(--accent)' }}>Register</Link>
                </div>
            </div>
        </div>
    );
};

export default Login;
