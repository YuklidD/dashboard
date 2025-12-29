import React, { useState } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import { register } from '../services/api';

const Register = () => {
    const [email, setEmail] = useState('');
    const [password, setPassword] = useState('');
    const [error, setError] = useState('');
    const [success, setSuccess] = useState('');
    const navigate = useNavigate();

    const handleSubmit = async (e) => {
        e.preventDefault();
        setError('');
        setSuccess('');
        try {
            await register(email, password);
            setSuccess('Registration successful! Redirecting to login...');
            setTimeout(() => {
                navigate('/login');
            }, 2000);
        } catch (err) {
            setError(err.response?.data?.detail || 'Registration failed');
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
                <h1 style={{ textAlign: 'center', marginBottom: '32px', color: 'var(--text-primary)' }}>Register</h1>
                {error && <div style={{ color: 'var(--danger)', marginBottom: '16px', textAlign: 'center' }}>{error}</div>}
                {success && <div style={{ color: 'var(--success)', marginBottom: '16px', textAlign: 'center' }}>{success}</div>}
                <form onSubmit={handleSubmit} style={{ display: 'flex', flexDirection: 'column', gap: '20px' }}>
                    <input
                        type="email"
                        placeholder="Email"
                        value={email}
                        onChange={(e) => setEmail(e.target.value)}
                        required
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
                        required
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
                        Sign Up
                    </button>
                </form>
                <div style={{ marginTop: '20px', textAlign: 'center', color: 'var(--text-secondary)' }}>
                    Already have an account? <Link to="/login" style={{ color: 'var(--accent)' }}>Login</Link>
                </div>
            </div>
        </div>
    );
};

export default Register;
