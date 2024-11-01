import React, { useState } from 'react';
import { useAuth } from './context/AuthContext';

const Login = ({ setShowLogin }) => {
    const [username, setUsername] = useState('');
    const [password, setPassword] = useState('');
    const [error, setError] = useState(null);
    const { setAuthenticated, setUserId } = useAuth(); // Get setAuthenticated and setUserId from AuthContext

    const handleLogin = async (event) => {
        event.preventDefault();
        setError(null);

        try {
            const response = await fetch('http://127.0.0.1:5000/api/login', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ username, password }),
            });

            if (response.ok) {
                const data = await response.json();
                setAuthenticated(true);
                setUserId(data.userId); // Set userId in AuthContext
            } else {
                const data = await response.json();
                setError(data.error || "An error occurred.");
            }
        } catch (error) {
            console.error("Error:", error);
            setError("An error occurred.");
        }
    };

    return (
        <div style={styles.container}>
            <h2 style={styles.header}>Login</h2>
            <form onSubmit={handleLogin} style={styles.form}>
                <input
                    type="text"
                    placeholder="Username"
                    value={username}
                    onChange={(e) => setUsername(e.target.value)}
                    required
                    style={styles.input}
                />
                <input
                    type="password"
                    placeholder="Password"
                    value={password}
                    onChange={(e) => setPassword(e.target.value)}
                    required
                    style={styles.input}
                />
                <button type="submit" style={styles.button}>Login</button>
                {error && <p style={styles.error}>{error}</p>}
            </form>
            <button onClick={() => setShowLogin(false)} style={styles.switchButton}>
                Don't have an account? Sign Up
            </button>
        </div>
    );
};

const styles = {
    container: {
        backgroundColor: '#f5f3f0',
        borderRadius: '10px',
        padding: '40px',
        width: '400px',
        margin: '50px auto',
        boxShadow: '0 4px 12px rgba(0, 0, 0, 0.1)',
        fontFamily: 'Arial, sans-serif',
        textAlign: 'center',
    },
    header: {
        color: '#4a3f35',
        marginBottom: '20px',
    },
    form: {
        display: 'flex',
        flexDirection: 'column',
        alignItems: 'center',
    },
    input: {
        width: '80%',
        padding: '10px',
        margin: '10px 0',
        borderRadius: '5px',
        border: '1px solid #ccc',
        fontSize: '16px',
        backgroundColor: '#fff',
    },
    button: {
        backgroundColor: '#4a3f35',
        color: '#fff',
        padding: '10px 20px',
        border: 'none',
        borderRadius: '5px',
        cursor: 'pointer',
        fontSize: '16px',
        marginTop: '10px',
        transition: 'background-color 0.3s',
    },
    switchButton: {
        backgroundColor: 'transparent',
        color: '#4a3f35',
        border: 'none',
        cursor: 'pointer',
        marginTop: '20px',
        fontSize: '14px',
        textDecoration: 'underline',
    },
    error: {
        color: 'red',
        marginTop: '10px',
    },
};

export default Login;
