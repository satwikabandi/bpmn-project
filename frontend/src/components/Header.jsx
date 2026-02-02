import React from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { Activity, LogOut, User } from 'lucide-react';
import { useAuth } from '../context/AuthContext';

const Header = () => {
    const { user, logout } = useAuth();
    const navigate = useNavigate();

    const handleLogout = () => {
        logout();
        navigate('/');
    };

    return (
        <header className="glass fixed w-full top-0 z-50">
            <div className="container" style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', height: '80px' }}>
                <Link to="/" style={{ display: 'flex', alignItems: 'center', gap: '0.75rem' }}>
                    <div style={{ background: 'linear-gradient(135deg, #3b82f6 0%, #8b5cf6 100%)', padding: '8px', borderRadius: '8px', display: 'flex' }}>
                        <Activity color="white" size={24} />
                    </div>
                    <span style={{ fontSize: '1.5rem', fontWeight: '700', letterSpacing: '-0.025em' }}>
                        BPMN<span style={{ color: '#3b82f6' }}>AI</span>
                    </span>
                </Link>

                <nav style={{ display: 'flex', gap: '1rem', alignItems: 'center' }}>
                    {user ? (
                        <>
                            <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', color: '#f8fafc' }}>
                                <User size={20} />
                                <span style={{ fontWeight: '500' }}>{user.username}</span>
                            </div>
                            <button onClick={handleLogout} className="btn btn-outline" style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', padding: '0.5rem 1rem' }}>
                                <LogOut size={16} /> Logout
                            </button>
                        </>
                    ) : (
                        <>
                            <Link to="/login" className="btn btn-outline">Log in</Link>
                            <Link to="/signup" className="btn btn-primary">Sign up</Link>
                        </>
                    )}
                </nav>
            </div>
        </header>
    );
};

export default Header;
