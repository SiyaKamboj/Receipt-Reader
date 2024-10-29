import React, { useState, useEffect } from 'react';
import { useAuth } from './context/AuthContext';

const ReceiptUpload = () => {
    const [view, setView] = useState("main");
    const [selectedItems, setSelectedItems] = useState([]);
    const [selectedFile, setSelectedFile] = useState(null);
    const [loading, setLoading] = useState(false);
    const [lineItems, setLineItems] = useState([]);
    const [subtotal, setSubtotal] = useState(0);
    const [tax, setTax] = useState(0);
    const [grandtotal, setGrandtotal] = useState(0);
    const [error, setError] = useState(null);
    const [receiptId, setReceiptId]=useState(0);
    const [vendorName, setVendorName]=useState(null);
    const [vendorAddress, setVendorAddress]=useState(null);
    const [purchaseTime, setPurchaseTime]=useState(new Date());
    const [receiptCompleted, setReceiptCompleted]= useState(false);
    const[selectedParticipants, setSelectedParticipants]= useState([]);

    const [myReceipts, setMyReceipts]=useState([]);
    const { userId } = useAuth();

    useEffect(() => {
        if (userId && receiptId) {
            console.log("calling fetchUserSelections")
            fetchUserSelections(userId, receiptId);
        }
    }, [userId, receiptId]); // Re-fetch selections whenever userId or receiptId changes

    
    useEffect(() => {
        // Trigger API call when view changes to "existing"
        if (view === "existing") {
            const fetchReceipts = async () => {
                try {
                    const response = await fetch('http://127.0.0.1:5000/api/MyReceipts', {
                        method: 'POST',
                        headers: {
                            'Content-Type': 'application/json',
                        },
                        body: JSON.stringify({ userId: userId }), // replace YOUR_USER_ID_HERE with the actual user ID
                    });
                    const data = await response.json();
                    setMyReceipts(data); // Update the receipts state with the fetched data
                } catch (error) {
                    console.error("Error fetching receipts:", error);
                }
            };
            fetchReceipts();
        } 
    }, [view]);

    const fetchUserSelections = async (userId, receiptId) => {
        try {
            setLoading(true);
            console.log("Fetching user selections...");
            const response = await fetch(`http://127.0.0.1:5000/api/getSelectedItems`, {
                method: 'POST', // Using POST method for sending data
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ user_id: userId, receipt_id: receiptId }) // Sending userId and receiptId in the body
            });
    
            // Check if the response is ok (status in the range 200-299)
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
    
            const data = await response.json(); // Parse the JSON data
            console.log("Selected items for receipt:", data.selected_items);
    
            // Set the selected items in the same way as before
            setSelectedItems(data.selected_items.map(item => item.id)); // Assuming you want to set selected item IDs
            console.log(selectedItems);
            setLoading(false);
        } catch (error) {
            console.error("Error fetching user selections:", error);
            setLoading(false);
        }
    };
    
    const handleSubmit = async (event) => {
        event.preventDefault();
        if (!selectedFile) return;

        setLoading(true);
        setError(null);

        const formData = new FormData();
        //pass userId to the backend so that you can change db appropirately
        formData.append('receipt_image', selectedFile);
        formData.append('userId', userId);
        console.log("appending userId as " + userId);

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
                setReceiptId(data.receipt_id);
                setVendorName(data.vendor_name);
                setVendorAddress(data.vendor_address);
                setPurchaseTime(data.date_of_purchase);
                setReceiptCompleted(data.completed);
            } else {
                setError(data.error || "An error occurred while processing the receipt.");
            }
        } catch (error) {
            console.error("Error:", error);
            setError("An error occurred while processing the receipt.");
        } finally {
            setLoading(false);
            setView("itemSelection");
        }
    };

    const handleSelectItem = (itemId) => {
        console.log(`Previous selected items:`, selectedItems);
        setSelectedItems((selectedItems) => {
            if (selectedItems.includes(itemId)) {
                // If the item is already selected, remove it
                console.log(`Item ${itemId} is now unchecked.`);
                return selectedItems.filter(item => item.id !== itemId);
            } else {
                // If the item is not selected, add it
                console.log(`Item ${itemId} is now checked.`);
                return [...selectedItems, itemId];
            }
        });
    };

    const handleDone = async () => {
        const selectedItems = lineItems.filter((item, index) => {
            const checkbox = document.querySelectorAll('input[type="checkbox"]')[index];
            return checkbox.checked;
        }).map(item => item.id);
    
        console.log("Selected items:", selectedItems);
        // Add your logic to handle the selected items here

        const payload = {
            selectedItems: selectedItems,
            userId: userId,
            receiptId: receiptId
        };
        try {
            const response = await fetch('http://127.0.0.1:5000/api/userChosen', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify(payload), //send id's
            });

            if (response.ok) {
                const responseData = await response.json();
                const readytomoveon= responseData.ready_to_move_on;
                console.log("ready to mvoe on is ", readytomoveon)
                console.log("Response data:", responseData);
                if (readytomoveon==true){
                    setView("split-cost");
                }
            } 
            else {
                console.error("Error:", response.statusText);
            }
        } catch (error) {
            console.error("Error:", error);
        }
    };
    
    const handleViewReceipt = async (receiptId) => {
        try {
            const response = await fetch('http://127.0.0.1:5000/api/getOneReceipt', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ receipt_id: receiptId }),
            });
    
            if (!response.ok) {
                throw new Error(`Error: ${response.statusText}`);
            }
    
            const data = await response.json();
            console.log("Receipt Data:", data);
            setLineItems(data.line_items);
            console.log('line items are '+ lineItems);
            setSubtotal(data.subtotal);
            console.log('subtotal is '+ subtotal);
            setTax(data.tax);
            setGrandtotal(data.grand_total);
            setReceiptId(data.receipt_id);
            setVendorName(data.vendor_name);
            setVendorAddress(data.vendor_address);
            setPurchaseTime(data.purchase_time);
            setReceiptCompleted(data.completed);
            // Here you can store the receipt data in state or context if needed
            // For example, you might want to store it in a global state
            // and then navigate to the item selection view
            // setSelectedReceipt(receiptData); // If you use context or state management
            
            // Redirect to the "itemSelection" view
            setView("itemSelection");
        } catch (error) {
            console.error("Failed to fetch receipt:", error);
        }
    };

    return (
        <div style={styles.container}>
            {view === "main" ? (
                <div>
                    <h2>Welcome! What would you like to do?</h2>
                    <button style={{ ...styles.button, marginRight: '50px' }} onClick={() => setView("upload")}>
                        Upload New Receipt
                    </button>
                    <button style={styles.button} onClick={() => setView("existing")}>
                        See Existing Receipts
                    </button>
                </div>
            ) : view === "upload" ? (
                <div>
                    <button style={{ ...styles.button}} onClick={() => setView("main")}>
                        Back
                    </button>
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
                </div>
            ) : view === "itemSelection" ? (
                <div>
                    {loading ? (
                        <div style={styles.loadingScreen}>
                            <h2 style={styles.loadingText}>Loading...</h2>
                        </div>
                    ) : lineItems.length > 0 ? (
                        <div>
                            <h2 style={styles.header}>{vendorName} Receipt Summary</h2>
                            <h3>
                                Completion Status: <span style={{ color: receiptCompleted ? 'green' : 'red' }}>
                                    {receiptCompleted ? 'Complete' : 'Incomplete'}
                                </span>
                            </h3>
                            <h4>{vendorAddress}</h4>
                            <h5>Purchased on: {purchaseTime}</h5>
                            <div style={styles.summarySection}>
                                <h3 style={styles.summaryText}>Subtotal: <span style={styles.price}>${subtotal}</span></h3>
                                <h3 style={styles.summaryText}>Tax: <span style={styles.price}>${tax}</span></h3>
                                <h3 style={styles.summaryText}>Grand Total: <span style={styles.price}>${grandtotal}</span></h3>
                            </div>
                            <h3 style={styles.itemsHeader}>Select Your Items</h3>
                            <div style={styles.itemList}>
                                {/* {lineItems.map((item, index) => (
                                    <div key={index} style={styles.row}>
                                        <input
                                            id={item.id}
                                            type="checkbox"
                                            style={styles.checkbox}
                                            checked={selectedItems.includes(item.id)}
                                            onChange={() => handleSelectItem(item.id)}
                                        />
                                        <span style={styles.itemName}>{item.description}</span>
                                        <span style={styles.itemPrice}>${item.price}</span>
                                    </div>
                                ))} */}
                                {lineItems.map((item) => (
                                    <div key={item.id} style={styles.row}>
                                        <input
                                            id={item.id}
                                            type="checkbox"
                                            style={styles.checkbox}
                                            checked={selectedItems.includes(item.id)} // Check if the item is selected
                                            onChange={() => handleSelectItem(item.id)}
                                        />
                                        <span style={styles.itemName}>{item.description}</span>
                                        <span style={styles.itemPrice}>${item.price}</span>
                                    </div>
                                ))}
                            </div>
                            <button style={{ ...styles.button, marginRight: '55px'}} onClick={() => setView("main")}>
                                Back
                            </button>
                            <button style={{ ...styles.button, marginRight: '55px'}} onClick={() => setView("collaborators")}>
                                Invite Collaborators
                            </button>
                            <button onClick={handleDone} style={{ ...styles.doneButton }}>Done</button>
                        </div>
                    ) : (
                        <p>No items found. Please try uploading again.</p>
                    )}
                </div>
            ) : view === "existing" ? (
                <div>
                    <h2>Existing Receipts</h2>
                    {myReceipts.length > 0 ? (
                        <ul>
                            {myReceipts.map((receipt) => (
                                <li key={receipt.receipt_id} style={styles.receiptItem}>
                                    <div>
                                        <h3>{receipt.vendor_name}</h3>
                                        <p>Purchase Time: {new Date(receipt.purchase_time).toLocaleString()}</p>
                                        <p>
                                            Completion Status: 
                                            <span style={{ color: receipt.completed ? 'green' : 'red' }}>
                                                {receipt.completed ? 'Complete' : 'Incomplete'}
                                            </span>
                                        </p>
                                        <button 
                                            style={styles.viewButton} 
                                            onClick={() => handleViewReceipt(receipt.receipt_id)}
                                        >
                                            View Receipt
                                        </button>
                                    </div>
                                </li>
                            ))}
                        </ul>
                    ) : (
                        <p>No receipts found.</p>
                    )}
                    <button style={styles.button} onClick={() => setView("main")}>
                        Back
                    </button>
                </div>
            ) : view === "split-cost" ? (
                <div>
                    <h2>Split Costs</h2>
                </div>
            ) : view === "collaborators" ? (
                <div>
                    <h2>Collaborators</h2>
                    <h3>Current Participants</h3>
                    <ul>
                        {currentParticipants.map(participant => (
                            <li key={participant.user_id}>{participant.user_id}</li> // Display usernames instead of IDs if possible
                        ))}
                    </ul>
                    
                    <h3>Add Participants</h3>
                    <div>
                        {allUsers.map(user => (
                            <div key={user.user_id}>
                                <input
                                    type="checkbox"
                                    checked={selectedUserIds.includes(user.user_id)}
                                    onChange={() => handleUserSelection(user.user_id)}
                                />
                                <span>{user.username}</span>
                            </div>
                        ))}
                    </div>
                    <button onClick={addParticipants}>Add Selected Participants</button>
                </div>
            ) : null}
        </div>
    );
};

const styles = {
    container: {
        backgroundColor: '#f5f3f0',
        borderRadius: '12px',
        padding: '40px',
        width: '450px',
        margin: '50px auto',
        boxShadow: '0 4px 12px rgba(0, 0, 0, 0.15)',
        fontFamily: 'Arial, sans-serif',
    },
    loadingScreen: {
        display: 'flex',
        justifyContent: 'center',
        alignItems: 'center',
        height: '200px',
    },
    loadingText: {
        color: '#4a3f35',
    },
    header: {
        color: '#4a3f35',
        fontSize: '1.5em',
        marginBottom: '20px',
    },
    summarySection: {
        backgroundColor: '#ece5da',
        borderRadius: '8px',
        padding: '15px',
        marginBottom: '25px',
        textAlign: 'left',
    },
    summaryText: {
        color: '#4a3f35',
        fontSize: '1.1em',
        display: 'flex',
        justifyContent: 'space-between',
        margin: '5px 0',
    },
    itemsHeader: {
        color: '#4a3f35',
        fontSize: '1.2em',
        marginTop: '20px',
        marginBottom: '10px',
    },
    itemList: {
        display: 'flex',
        flexDirection: 'column',
        alignItems: 'flex-start',
    },
    row: {
        display: 'flex',
        alignItems: 'center',
        padding: '10px 0',
        width: '100%',
        borderBottom: '1px solid #ddd',
    },
    checkbox: {
        marginRight: '10px',
    },
    itemName: {
        flex: '1',
        fontSize: '1em',
        color: '#4a3f35',
    },
    itemPrice: {
        fontSize: '1em',
        color: '#4a3f35',
        textAlign: 'right',
        width: '80px',
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
    doneButton: {
        backgroundColor: '#4a3f35',
        color: '#fff',
        padding: '10px 20px',
        border: 'none',
        borderRadius: '5px',
        cursor: 'pointer',
        fontSize: '16px',
        marginTop: '20px',
        transition: 'background-color 0.3s',
    },
    error: {
        color: 'red',
        marginTop: '10px',
    },
};

export default ReceiptUpload;