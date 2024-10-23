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
        <div>
            {loading ? (
                <div className="loading-screen">
                    <h2>Loading...</h2>
                </div>
            ) : lineItems.length > 0 ? (
                <div>
                    <h2>Receipt Summary</h2>
                    <h3>Subtotal: ${subtotal.toFixed(2)}</h3>
                    <h3>Tax: ${tax.toFixed(2)}</h3>
                    <h3>Grand Total: ${grandtotal.toFixed(2)}</h3>
                    <h3>Items:</h3>
                    <ul>
                        {lineItems.map((item, index) => (
                            <li key={index}>
                                {item.description} - ${item.total}
                            </li>
                        ))}
                    </ul>
                </div>
            ) : (
                <form onSubmit={handleSubmit}>
                    <input 
                        type="file" 
                        accept="image/*" 
                        onChange={(e) => setSelectedFile(e.target.files[0])} 
                        required
                    />
                    <button type="submit">Upload Receipt</button>
                    {error && <p style={{ color: 'red' }}>{error}</p>}
                </form>
            )}
        </div>
    );
};

export default ReceiptUpload;
