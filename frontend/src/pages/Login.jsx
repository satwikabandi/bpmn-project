import React, { useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { ArrowLeft } from 'lucide-react';
import { useAuth } from '../context/AuthContext';

const Login = () => {
    const [email, setEmail] = useState('');
    const [password, setPassword] = useState('');
    const [error, setError] = useState('');
    const { login } = useAuth();
    const navigate = useNavigate();

    const handleSubmit = async (e) => {
        e.preventDefault();
        setError('');

        try {
            const response = await fetch('http://127.0.0.1:8000/api/auth/login/', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ username: email, password }),
            });

            const data = await response.json();

            if (response.ok) {
                login(data.user, data.token);
                navigate('/');
            } else {
                setError(data.error || 'Login failed');
            }
        } catch {
            setError('Something went wrong. Please try again.');
        }
    };

    return (
        <div style={{ minHeight: '100vh', display: 'flex', alignItems: 'center', justifyContent: 'center', paddingTop: '80px', paddingBottom: '2rem' }}>
            <div className="glass" style={{ width: '100%', maxWidth: '400px', padding: '2rem', borderRadius: '1rem' }}>
                <Link to="/" style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', color: '#94a3b8', marginBottom: '2rem', fontSize: '0.9rem' }}>
                    <ArrowLeft size={16} /> Back to Home
                </Link>

                <h2 style={{ fontSize: '2rem', fontWeight: '700', marginBottom: '0.5rem' }}>Welcome back</h2>
                <p style={{ color: '#94a3b8', marginBottom: '2rem' }}>Please enter your details to sign in.</p>

                {error && <div style={{ color: '#ef4444', marginBottom: '1rem', padding: '0.5rem', background: 'rgba(239, 68, 68, 0.1)', borderRadius: '0.5rem' }}>{error}</div>}

                <form onSubmit={handleSubmit}>
                    <div style={{ marginBottom: '1.5rem' }}>
                        <label style={{ display: 'block', fontSize: '0.9rem', fontWeight: '500', marginBottom: '0.5rem' }}>Email or Username</label>
                        <input
                            type="text"
                            required
                            style={{ width: '100%', padding: '0.75rem', borderRadius: '0.5rem', background: '#0f172a', border: '1px solid #334155', color: 'white', outline: 'none' }}
                            value={email}
                            onChange={(e) => setEmail(e.target.value)}
                        />
                    </div>

                    <div style={{ marginBottom: '1.5rem' }}>
                        <label style={{ display: 'block', fontSize: '0.9rem', fontWeight: '500', marginBottom: '0.5rem' }}>Password</label>
                        <input
                            type="password"
                            required
                            style={{ width: '100%', padding: '0.75rem', borderRadius: '0.5rem', background: '#0f172a', border: '1px solid #334155', color: 'white', outline: 'none' }}
                            value={password}
                            onChange={(e) => setPassword(e.target.value)}
                        />
                    </div>

                    <button type="submit" className="btn btn-primary" style={{ width: '100%', marginBottom: '1.5rem' }}>Sign in</button>
                </form>

                <p style={{ textAlign: 'center', color: '#94a3b8', fontSize: '0.9rem' }}>
                    Don't have an account? <Link to="/signup" style={{ color: '#3b82f6', fontWeight: '500' }}>Sign up</Link>
                </p>
            </div>
        </div>
    );
};

export default Login;
