import React, { useState } from 'react';
import Login from './components/Login';
import ReceiptUpload from './components/ReceiptUpload';

const App = () => {
    const [isAuthenticated, setAuthenticated] = useState(false);

    return (
        <div>
            {isAuthenticated ? (
                <ReceiptUpload />
            ) : (
                <Login setAuthenticated={setAuthenticated} />
            )}
        </div>
    );
};

export default App;
