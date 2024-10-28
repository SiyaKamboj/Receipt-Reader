import React, { useState } from 'react';

const SignUp = ({ setShowLogin }) => {
    const [username, setUsername] = useState('');
    const [email, setEmail] = useState('');
    const [password, setPassword] = useState('');
    const [phoneNumber, setPhoneNumber] = useState('');
    const [error, setError] = useState(null);

    const handleSignUp = async (event) => {
        event.preventDefault();
        setError(null);

        try {
            const response = await fetch('http://127.0.0.1:5000/api/register', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ username, email, password, phoneNumber }),
            });

            if (response.ok) {
                alert("Registration successful! Please log in.");
                setShowLogin(true); // Switch to login view after successful registration
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
            <h2 style={styles.header}>Sign Up</h2>
            <form onSubmit={handleSignUp} style={styles.form}>
                <input
                    type="text"
                    placeholder="Username"
                    value={username}
                    onChange={(e) => setUsername(e.target.value)}
                    required
                    style={styles.input}
                />
                <input
                    type="email"
                    placeholder="Email"
                    value={email}
                    onChange={(e) => setEmail(e.target.value)}
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
                <input
                    type="text"
                    placeholder="Phone Number"
                    value={phoneNumber}
                    onChange={(e) => setPhoneNumber(e.target.value)}
                    style={styles.input}
                />
                <button type="submit" style={styles.button}>Sign Up</button>
                {error && <p style={styles.error}>{error}</p>}
            </form>
        </div>
    );
};

const styles = {
    container: {
        backgroundColor: '#f5f3f0', // Light neutral background
        borderRadius: '10px',
        padding: '40px',
        width: '400px',
        margin: '50px auto',
        boxShadow: '0 4px 12px rgba(0, 0, 0, 0.1)',
        fontFamily: 'Arial, sans-serif',
        textAlign: 'center',
    },
    header: {
        color: '#4a3f35', // Dark brown header text
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
        backgroundColor: '#fff', // White input background
    },
    button: {
        backgroundColor: '#4a3f35', // Dark brown button
        color: '#fff',
        padding: '10px 20px',
        border: 'none',
        borderRadius: '5px',
        cursor: 'pointer',
        fontSize: '16px',
        marginTop: '10px',
        transition: 'background-color 0.3s',
    },
    buttonHover: {
        backgroundColor: '#3a2f25',
    },
    error: {
        color: 'red',
        marginTop: '10px',
    },
};

export default SignUp;
