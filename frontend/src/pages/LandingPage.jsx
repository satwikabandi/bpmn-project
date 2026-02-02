import React from 'react';
import { motion } from 'framer-motion';
import { Workflow, Zap, FileText } from 'lucide-react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';

const LandingPage = () => {
    const { user } = useAuth();
    const navigate = useNavigate();

    const handleStartConverting = () => {
        if (user) {
            navigate('/dashboard');
        } else {
            navigate('/login');
        }
    };

    const containerVariants = {
        hidden: { opacity: 0 },
        visible: {
            opacity: 1,
            transition: { staggerChildren: 0.2 }
        }
    };

    const itemVariants = {
        hidden: { y: 20, opacity: 0 },
        visible: { y: 0, opacity: 1 }
    };

    return (
        <div style={{ paddingTop: '80px', minHeight: '100vh' }}>
            {/* Hero Section */}
            <section style={{ padding: '6rem 0', textAlign: 'center', position: 'relative', overflow: 'hidden' }}>
                <div className="container">
                    <motion.div
                        initial="hidden"
                        animate="visible"
                        variants={containerVariants}
                    >
                        <motion.h1 variants={itemVariants} style={{ fontSize: '4rem', fontWeight: '800', marginBottom: '1.5rem', lineHeight: '1.1' }}>
                            Text to <span style={{ background: '-webkit-linear-gradient(45deg, #3b82f6, #8b5cf6)', WebkitBackgroundClip: 'text', WebkitTextFillColor: 'transparent' }}>BPMN</span><br />
                            Made Instant.
                        </motion.h1>
                        <motion.p variants={itemVariants} style={{ fontSize: '1.25rem', color: '#94a3b8', maxWidth: '600px', margin: '0 auto 2.5rem' }}>
                            Transform your process descriptions into professional Business Process Model and Notation diagrams in seconds using advanced AI.
                        </motion.p>
                        <motion.div variants={itemVariants} style={{ display: 'flex', gap: '1rem', justifyContent: 'center' }}>
                            <button
                                onClick={handleStartConverting}
                                className="btn btn-primary"
                                style={{ padding: '1rem 2rem', fontSize: '1.1rem' }}
                            >
                                Start Converting Now
                            </button>
                        </motion.div>
                    </motion.div>
                </div>

                {/* Abstract Background Elements */}
                <div style={{ position: 'absolute', top: '20%', left: '10%', width: '300px', height: '300px', background: 'radial-gradient(circle, rgba(59,130,246,0.1) 0%, rgba(0,0,0,0) 70%)', zIndex: -1 }}></div>
                <div style={{ position: 'absolute', bottom: '10%', right: '10%', width: '400px', height: '400px', background: 'radial-gradient(circle, rgba(139,92,246,0.1) 0%, rgba(0,0,0,0) 70%)', zIndex: -1 }}></div>
            </section>

            {/* Explanation Section */}
            <section style={{ padding: '6rem 0', background: '#1e293b' }}>
                <div className="container">
                    <div style={{ textAlign: 'center', marginBottom: '4rem' }}>
                        <h2 style={{ fontSize: '2.5rem', marginBottom: '1rem', fontWeight: '700' }}>Why BPMN Matters</h2>
                        <p style={{ color: '#94a3b8', fontSize: '1.1rem' }}>Understanding the power of visual process modeling</p>
                    </div>

                    <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(300px, 1fr))', gap: '2rem' }}>
                        <div className="glass" style={{ padding: '2rem', borderRadius: '1rem' }}>
                            <div style={{ background: 'rgba(59, 130, 246, 0.1)', width: 'fit-content', padding: '1rem', borderRadius: '1rem', marginBottom: '1.5rem', color: '#3b82f6' }}>
                                <Workflow size={32} />
                            </div>
                            <h3 style={{ fontSize: '1.5rem', marginBottom: '1rem', fontWeight: '600' }}>Standardized Clarity</h3>
                            <p style={{ color: '#94a3b8', lineHeight: '1.7' }}>
                                BPMN (Business Process Model and Notation) provides a standard graphical notation that is readily understandable by all business stakeholders.
                            </p>
                        </div>

                        <div className="glass" style={{ padding: '2rem', borderRadius: '1rem' }}>
                            <div style={{ background: 'rgba(139, 92, 246, 0.1)', width: 'fit-content', padding: '1rem', borderRadius: '1rem', marginBottom: '1.5rem', color: '#8b5cf6' }}>
                                <Zap size={32} />
                            </div>
                            <h3 style={{ fontSize: '1.5rem', marginBottom: '1rem', fontWeight: '600' }}>Efficiency & Optimization</h3>
                            <p style={{ color: '#94a3b8', lineHeight: '1.7' }}>
                                Visualizing processes helps identify bottlenecks, redundancies, and inefficiencies. It bridges the gap between process design and implementation.
                            </p>
                        </div>

                        <div className="glass" style={{ padding: '2rem', borderRadius: '1rem' }}>
                            <div style={{ background: 'rgba(16, 185, 129, 0.1)', width: 'fit-content', padding: '1rem', borderRadius: '1rem', marginBottom: '1.5rem', color: '#10b981' }}>
                                <FileText size={32} />
                            </div>
                            <h3 style={{ fontSize: '1.5rem', marginBottom: '1rem', fontWeight: '600' }}>Documentation</h3>
                            <p style={{ color: '#94a3b8', lineHeight: '1.7' }}>
                                Serves as a living documentation of your business rules and workflows, ensuring consistency and compliance across your organization.
                            </p>
                        </div>
                    </div>
                </div>
            </section>
        </div>
    );
};

export default LandingPage;
