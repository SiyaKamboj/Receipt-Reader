import React, { useState } from 'react';
import Login from './components/Login';
import SignUp from './components/SignUp';
import ReceiptUpload from './components/ReceiptUpload';
import { AuthProvider, useAuth } from './components/context/AuthContext'; // Import AuthProvider and useAuth

const AppContent = () => {
    const [showLogin, setShowLogin] = useState(true);
    const { authenticated } = useAuth(); // Get authenticated status from context

    return (
        <div>
            {authenticated ? (
                <ReceiptUpload />
            ) : showLogin ? (
                <Login setShowLogin={setShowLogin} />
            ) : (
                <SignUp setShowLogin={setShowLogin} />
            )}
        </div>
    );
};

const App = () => {
    return (
        <AuthProvider>
            <AppContent />
        </AuthProvider>
    );
};

export default App;
