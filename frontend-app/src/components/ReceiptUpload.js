import React, { useState } from 'react';

const ReceiptUpload = () => {
    const [selectedFile, setSelectedFile] = useState(null);
    const [loading, setLoading] = useState(false);
    const [lineItems, setLineItems] = useState([]);
    const [subtotal, setSubtotal] = useState(0);
    const [tax, setTax] = useState(0);
    const [grandtotal, setGrandtotal] = useState(0);
    const [error, setError] = useState(null);

    const handleSubmit = async (event) => {
        event.preventDefault();
        if (!selectedFile) return;

        setLoading(true);
        setError(null);

        const formData = new FormData();
        formData.append('receipt_image', selectedFile);

        try {
            const response = await fetch('http://127.0.0.1:5000/api/itemized-receipt', {
                method: 'POST',
                body: formData,
            });

            const data = await response.json();
            if (response.ok) {
                setLineItems(data.line_items);
                setSubtotal(data.subtotal);
                setTax(data.tax);
                setGrandtotal(data.grandtotal);
            } else {
                setError(data.error || "An error occurred while processing the receipt.");
            }
        } catch (error) {
            console.error("Error:", error);
            setError("An error occurred while processing the receipt.");
        } finally {
            setLoading(false);
        }
    };

    return (
        <div style={styles.container}>
            {loading ? (
                <div style={styles.loadingScreen}>
                    <h2 style={styles.loadingText}>Loading...</h2>
                </div>
            ) : lineItems.length > 0 ? (
                <div>
                    <h2 style={styles.header}>Receipt Summary</h2>
                    <h3 style={styles.summaryText}>Subtotal: ${subtotal.toFixed(2)}</h3>
                    <h3 style={styles.summaryText}>Tax: ${tax.toFixed(2)}</h3>
                    <h3 style={styles.summaryText}>Grand Total: ${grandtotal.toFixed(2)}</h3>
                    <h3 style={styles.itemsHeader}>Items:</h3>
                    <ul style={styles.itemList}>
                        {lineItems.map((item, index) => (
                            <li key={index} style={styles.item}>
                                {item.description} - ${item.total}
                            </li>
                        ))}
                    </ul>
                </div>
            ) : (
                <form onSubmit={handleSubmit} style={styles.form}>
                    <input 
                        type="file" 
                        accept="image/*" 
                        onChange={(e) => setSelectedFile(e.target.files[0])} 
                        required
                        style={styles.fileInput}
                    />
                    <button type="submit" style={styles.button}>Upload Receipt</button>
                    {error && <p style={styles.error}>{error}</p>}
                </form>
            )}
        </div>
    );
};

const styles = {
    container: {
        backgroundColor: '#f5f3f0', // Light beige background
        borderRadius: '10px',
        padding: '40px',
        width: '400px',
        margin: '50px auto',
        boxShadow: '0 4px 12px rgba(0, 0, 0, 0.1)',
        fontFamily: 'Arial, sans-serif',
        textAlign: 'center',
    },
    loadingScreen: {
        display: 'flex',
        justifyContent: 'center',
        alignItems: 'center',
        height: '200px',
    },
    loadingText: {
        color: '#4a3f35', // Dark brown loading text
    },
    header: {
        color: '#4a3f35', // Dark brown header
        marginBottom: '20px',
    },
    summaryText: {
        color: '#4a3f35', // Dark brown text for totals
        margin: '5px 0',
    },
    itemsHeader: {
        color: '#4a3f35',
        marginTop: '20px',
    },
    itemList: {
        listStyleType: 'none',
        padding: 0,
        color: '#000', // Black item text
    },
    item: {
        margin: '5px 0',
        color: '#4a3f35',
    },
    form: {
        display: 'flex',
        flexDirection: 'column',
        alignItems: 'center',
    },
    fileInput: {
        padding: '10px',
        margin: '10px 0',
        borderRadius: '5px',
        border: '1px solid #ccc',
        fontSize: '16px',
        backgroundColor: '#fff',
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

export default ReceiptUpload;
