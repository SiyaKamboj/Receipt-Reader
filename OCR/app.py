import json
from flask import Flask, jsonify, request
#from runmodel import passToApi
from flask_cors import CORS
import requests
import base64
from flask_sqlalchemy import SQLAlchemy
import os
from models import Receipt, ReceiptItem, User, UserItemSelection, ReceiptParticipant, db
from collections import defaultdict

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///receipts.db'  # Using SQLite for simplicity
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db.init_app(app) #initialzie db from models.py with app
CORS(app)
#CORS(app, resources={r"/api/*": {"origins": "http://localhost:3000", "methods": ["GET", "POST", "OPTIONS"], "allow_headers": ["Content-Type", "Authorization"]}})

with app.app_context():
    db.create_all() # Creates tables if they don't exist

def getItemizedData():
    # Load itemized data from a local JSON file for testing
    with open("response1.json", "r") as f:
        data = json.load(f)
    items = data['receipts'][0]['items']
    return items

@app.route('/api/itemized-receipt', methods=['POST'])
def itemize_receipt():
    from dateutil import parser
    user_id = request.form.get('userId')
    print("User_id is "+ user_id)
    # Assuming receipt_image is sent in the POST request
    if 'receipt_image' in request.files:
        receipt_image = request.files['receipt_image']
        receipt_image_name = receipt_image.filename

        # Check if receipt already exists in the database BY CHECKING IF TIMESTAMP OF PURCHASE AND STORE NAME ARE THE SAME
        existing_receipt = Receipt.query.filter_by(receipt_image_name=receipt_image_name).first()
        #existing_receipt=True
        
        if existing_receipt:
            print("existing receipt!!!")
            #get receipt id so u can query items table
            receipt_id=existing_receipt.receipt_id
            #get all items with certain receipt id
            items = db.session.query(ReceiptItem.description, ReceiptItem.price, ReceiptItem.item_id).filter_by(receipt_id=receipt_id).all()
            # Converting to a list of dictionaries for easier handling on the frontend
            item_list = [{"description": item.description, "price": item.price, "id": item.item_id} for item in items]

            #TODO DONE : change this to query line items in the other table
            return jsonify({
                "subtotal": existing_receipt.subtotal,
                "line_items": item_list,
                "tax": existing_receipt.tax,
                "grandtotal": existing_receipt.grand_total,
                "receipt_id": receipt_id,
                "vendor_name": existing_receipt.vendor_name,
                "vendor_address": existing_receipt.vendor_address,
                "date_of_purchase": existing_receipt.purchase_time,
                "completed": existing_receipt.completed
            })

        try:
            print("SUCCESSFULLY CALLED")

            #for calling api (which I have a free trial for)
            url = "https://api.veryfi.com/api/v8/partner/documents"
            file_data = receipt_image.read()  # Read as binary
            encoded_file = base64.b64encode(file_data).decode('utf-8')  # Encode to base64 and decode to string
            # Prepare the payload with the base64 encoded file
            payload = {
                "file_data": encoded_file,  # Use the correct field name as per the API documentation
            }
            headers = {
                'Accept': 'application/json',
                'CLIENT-ID': 'vrfXaU21wAPkSJ838vRCtayv4MAwjoBZnBrEEwG',
                'AUTHORIZATION': 'apikey siyakamboj20:a0fe4ffe54af95a46a674150872e891e'
            }
            response = requests.request("POST", url, headers=headers, data=json.dumps(payload))
            print(response.status_code)
            print(response.text)
            receipt = json.loads(response.text)

            # receipt=json.loads("apiresponse.json")
            line_items = receipt.get("line_items", [])
            subtotal = receipt.get("subtotal")
            tax = receipt.get("tax")
            grandtotal = receipt.get("total")
            vendor_name = receipt["vendor"].get("name")
            vendor_address = receipt["vendor"].get("address")
            if receipt.get("date") is not None:
                dateOfPurchase = parser.parse(receipt.get("date"))
            else:
                dateOfPurchase=None




            # Store the result in the database
            #TODO: upload user_id into here, remove line_items
            print("user_id is "+ user_id)
            new_receipt = Receipt(
                uploaded_by= user_id, 
                receipt_image_name=receipt_image_name,
                vendor_name=vendor_name,
                vendor_address=vendor_address,
                purchase_time=dateOfPurchase,
                subtotal=subtotal,
                tax=tax,
                grand_total=grandtotal, 
                completed=False
            )
            db.session.add(new_receipt)
            db.session.commit()
            receipt_id = new_receipt.receipt_id
            
            #save each item from lineitems into ReceiptItem table
            for item in line_items:
                new_item= ReceiptItem(
                    receipt_id= receipt_id,
                    description= item.get("description"),
                    price=item.get("total")
                )
                db.session.add(new_item)
            db.session.commit()


            #for debugging purposes
            for item in line_items:
                description = item.get("description")
                total = item.get("total")
                print(f"Item: {description}, \tCost: ${total:.2f}")
            print(f"Subtotal: ${subtotal:.2f}")
            print(f"Tax: ${tax:.2f}")
            print(f"Grand Total: ${grandtotal:.2f}")
            print(f"Vendor Name: {vendor_name}")
            print(f"Vendor address: {vendor_address}")
            print(f"Date of purchase: {dateOfPurchase}")

            #get all items and their ID's and return it to the front-end
            items = db.session.query(ReceiptItem.description, ReceiptItem.price, ReceiptItem.item_id).filter_by(receipt_id=receipt_id).all()
            # Converting to a list of dictionaries for easier handling on the frontend
            item_list = [{"description": item.description, "price": item.price, "id": item.item_id} for item in items]

            #TODO : update the jsonify
            return jsonify({
                "line_items": item_list,
                "subtotal": subtotal,
                "tax": tax,
                "grandtotal": grandtotal,
                "receipt_id": receipt_id,
                "vendor_name": vendor_name,
                "vendor_address": vendor_address,
                "date_of_purchase": dateOfPurchase, 
                "completed": False
            })
        except Exception as e:
            print(f"Error processing file: {str(e)}")  # Log the error for debugging
            return jsonify({"error": "Failed to process file"}), 500

@app.route('/api/register', methods=['POST'])
def register():
    data = request.get_json()
    username = data.get('username')
    email = data.get('email')
    password = data.get('password')
    phone_number = data.get('phoneNumber')

    print("called 2")

    if User.query.filter_by(username=username).first():
        return jsonify({"error": "Username already exists."}), 400

    new_user = User(username=username, email=email)
    #new_user.password("hello")
    new_user.set_password(password)
    new_user.phone_number = phone_number
    db.session.add(new_user)
    db.session.commit()
    return jsonify({"message": "User registered successfully."}), 201
    #return 201

@app.route('/api/login', methods=['POST'])
def login():
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')

    user = User.query.filter_by(username=username).first()
    if user and user.check_password(password):
        return jsonify({
        "message": "Login successful.",
        "userId": user.user_id 
    }), 200
    return jsonify({"error": "Invalid username or password."}), 401

@app.route('/api/userChosen', methods=['POST'])
def userChoosesItems():
    data=request.get_json()
    selected_items = data.get('selectedItems', [])
    user_id = data.get('userId')
    receipt_id=data.get('receiptId')
    # Debugging print statements
    print("Selected item IDs received:", selected_items)
    print("User ID received:", user_id)
    print("Receipt ID received", receipt_id)
    # first delete everything associated with that user id and receipt id in the table
    db.session.query(UserItemSelection).filter_by(user_id=user_id, receipt_id=receipt_id).delete()
    db.session.commit()

    #insert user id and item id into table
    for item in selected_items:
        new_user_Item_Connection= UserItemSelection(
            user_id=user_id,
            item_id=item, 
            receipt_id=receipt_id
        )
        db.session.add(new_user_Item_Connection)
    db.session.commit()

    ready_to_move_on= check_all_items_selected(receipt_id)

    return jsonify({
        "message": "Successfully connected user with item",
        "ready_to_move_on": ready_to_move_on
    }), 200

#make sure all items, given a receipt id, are accounted for in the selected_item_id. this will determine whether you can move on and split costs or not
def check_all_items_selected(receipt_id):
    # Step 1: Get all item_ids for the specified receipt_id from the ReceiptItem table
    receipt_item_ids = {item.item_id for item in db.session.query(ReceiptItem.item_id).filter_by(receipt_id=receipt_id).all()}
    
    # Step 2: Get all item_ids for the specified receipt_id from the UserItemSelection table
    selected_item_ids = {selection.item_id for selection in db.session.query(UserItemSelection.item_id).filter_by(receipt_id=receipt_id).all()}
    
    # Step 3: Check if every item_id in ReceiptItem is in UserItemSelection
    if receipt_item_ids.issubset(selected_item_ids):
        #change completed in this receipt_id to true
        receipt = Receipt.query.get(receipt_id)
        receipt.completed = True
        db.session.commit()
        return True
    else:
        #change completed in this receipt_id to false
        receipt = Receipt.query.get(receipt_id)
        receipt.completed = False
        db.session.commit()
        return False

@app.route('/api/MyReceipts', methods=['POST'])
def getAllMyReceipts():
    data=request.get_json()
    user_id = data.get('userId')
    if user_id is None:
        return jsonify({"error": "userId is required"}), 400
    # Query the database for receipts uploaded by the specified user
    receipts = Receipt.query.filter_by(uploaded_by=user_id).with_entities(Receipt.receipt_id, Receipt.receipt_image_name, Receipt.vendor_name, Receipt.purchase_time, Receipt.completed).all()
    # Format the results as a list of dictionaries
    result = [{"receipt_id": receipt.receipt_id, "name": receipt.receipt_image_name, "vendor_name": receipt.vendor_name, "purchase_time": receipt.purchase_time, "completed": receipt.completed} for receipt in receipts]
    return jsonify(result), 200

@app.route('/api/getOneReceipt', methods=['POST'])
def getOneReceipt():
    data=request.get_json()
    receipt_id=data.get('receipt_id')
    print('receipt_id is ', receipt_id)
    if receipt_id is None:
        return jsonify({"error":"receiptId is required"}), 400
    
    # Retrieve the receipt object
    receipt = Receipt.query.filter_by(receipt_id=receipt_id).first()

    # Check if the receipt was found
    if receipt is None:
        return jsonify({"error": "Receipt not found"}), 404

    # Get all items associated with the receipt
    items = db.session.query(ReceiptItem.description, ReceiptItem.price, ReceiptItem.item_id).filter_by(receipt_id=receipt_id).all()

    # Convert items to a list of dictionaries for easier handling on the frontend
    item_list = [{"description": item.description, "price": item.price, "id": item.item_id} for item in items]

    # Prepare the result with all necessary receipt information
    result = {
        "line_items": item_list,
        "receipt_id": receipt.receipt_id,
        "name": receipt.receipt_image_name,
        "vendor_name": receipt.vendor_name,
        "vendor_address": receipt.vendor_address,
        "purchase_time": receipt.purchase_time,
        "subtotal": receipt.subtotal,
        "tax": receipt.tax,
        "grand_total": receipt.grand_total,
        "completed": receipt.completed
    }

    # Return the result
    return jsonify(result), 200

@app.route('/api/getSelectedItems', methods=['POST'])
def get_selected_items():
    data = request.get_json()
    user_id = data.get('user_id')
    receipt_id = data.get('receipt_id')

    if user_id is None or receipt_id is None:
        return jsonify({"error": "user_id and receipt_id are required"}), 400
    # Step 1: Query the UserItemSelection table for the specified user_id and receipt_id
    selections = UserItemSelection.query.filter_by(user_id=user_id, receipt_id=receipt_id).all()
    # Step 2: Extract item_ids from the selections
    selected_item_ids = [selection.item_id for selection in selections]
    # Step 3: Query the ReceiptItem table for the selected item_ids
    items = ReceiptItem.query.filter(ReceiptItem.item_id.in_(selected_item_ids)).all()
    # Step 4: Convert the results to a list of dictionaries
    item_list = [{"description": item.description, "price": item.price, "id": item.item_id} for item in items]

    return jsonify({"selected_items": item_list}), 200

@app.route('/api/addParticipants', methods=['POST'])
def add_users_to_receipt():
    data = request.get_json()  # Get the JSON data sent in the request

    receipt_id = data.get('receipt_id')  # Extract receipt_id from the data
    user_ids = data.get('user_ids')  # Extract user_ids from the data

    if not receipt_id or not user_ids:
        return jsonify({"message": "Receipt ID and user IDs are required."}), 400

    # Check for duplicate entries and add new participants
    added_participants = []
    for user_id in user_ids:
        # Ensure that the combination of receipt_id and user_id is unique
        if not ReceiptParticipant.query.filter_by(receipt_id=receipt_id, user_id=user_id).first():
            new_participant = ReceiptParticipant(receipt_id=receipt_id, user_id=user_id)
            db.session.add(new_participant)
            added_participants.append(new_participant.user_id)

    try:
        db.session.commit()  # Commit the changes to the database
        return jsonify({"message": "Participants added successfully.", "added_participants": added_participants}), 201
    except Exception as e:
        db.session.rollback()  # Rollback in case of error
        return jsonify({"message": "An error occurred while adding participants.", "error": str(e)}), 500

@app.route('/api/getAllUsers', methods=['GET'])
def get_all_users():
    try:
        current_user_id = request.args.get('currentUserId', type=int)  # Get current user ID from query parameters
        all_users = User.query.filter(User.user_id != current_user_id).all()  # Exclude the current user

        # Convert the results to a list of dictionaries
        result = [{"user_id": user.user_id, "username": user.username, "email": user.email, "phone_number": user.phone_number} for user in all_users]

        return jsonify(users=result)
    except Exception as e:
        return jsonify({"message": "An error occurred while retrieving users.", "error": str(e)}), 500
    
@app.route('/api/getUserReceiptsParticipants', methods=['POST'])
def get_user_receipts_participants():
    try:
        data=request.get_json()
        user_id = data.get('userId')
        if user_id is None:
            return jsonify({"error": "userId is required"}), 400
        # Query the ReceiptParticipant table to get all receipt IDs for the specified user_id
        participant_receipts = ReceiptParticipant.query.filter_by(user_id=user_id).all()

        # Extract the receipt IDs
        receipt_ids = [participant.receipt_id for participant in participant_receipts]

        # Optionally, retrieve more details about the receipts from the Receipts table
        # for receipt_id in receipt_ids:
        #     receipts += getOneReceipt(receipt_id)
        receipts = Receipt.query.filter(Receipt.receipt_id.in_(receipt_ids)).with_entities(
            Receipt.receipt_id,
            Receipt.receipt_image_name,
            Receipt.vendor_name,
            Receipt.purchase_time,
            Receipt.completed
        ).all()

        # Convert the results to a list of dictionaries with relevant receipt info
        result = [{"receipt_id": receipt.receipt_id, "name": receipt.receipt_image_name, "vendor_name": receipt.vendor_name, "purchase_time": receipt.purchase_time, "completed": receipt.completed} for receipt in receipts]

        return jsonify(receipts=result), 200
    except Exception as e:
        return jsonify({"message": "An error occurred while retrieving all participating receipts.", "error": str(e)}), 500

@app.route('/api/SplitAmounts', methods=['POST'])
def calculate_amount_owed():
    try:
        data = request.get_json()
        receipt_id = data.get('receipt_id')
        
        # Retrieve receipt details
        receipt = Receipt.query.get(receipt_id)
        if not receipt:
            return jsonify({"error": "Receipt not found"}), 404
        subtotal = float(receipt.subtotal)
        grand_total = float(receipt.grand_total)
        
        # Calculate additional costs
        additional_costs = grand_total - subtotal
        
        # Retrieve item selections for the receipt
        selections = UserItemSelection.query.filter_by(receipt_id=receipt_id).all()
        
        # Step 1: Track each item's participants and divide item costs among them
        item_shares = defaultdict(list)  # Maps each item to the list of user_ids that selected it
        user_subtotals = defaultdict(float)  # Tracks each user's subtotal contribution
        
        for selection in selections:
            user_id = selection.user_id
            item_id = selection.item_id
            item_price = float(selection.item.price)
            
            # Add user to the list of participants for this item
            item_shares[item_id].append(user_id)
        
        # Step 2: Divide item prices among participants and accumulate to each user's subtotal
        for item_id, participants in item_shares.items():
            item_price = float(ReceiptItem.query.get(item_id).price)
            share_price = item_price / len(participants)  # Divide the item price among participants
            
            # Distribute share of item price to each user
            for user_id in participants:
                user_subtotals[user_id] += share_price

        # Step 3: Calculate each user's share of additional costs based on their subtotal percentage
        user_final_amounts = {}
        for user_id, user_subtotal in user_subtotals.items():
            # Calculate user's share of the additional costs
            additional_cost_share = (user_subtotal / subtotal) * additional_costs if subtotal > 0 else 0
            # Total amount owed by each user
            total_owed = round(user_subtotal + additional_cost_share, 2)

            # Retrieve user name
            user = User.query.get(user_id)
            user_name = user.username if user else "Unknown User"
            user_final_amounts[user_name] = total_owed

        # Check if calculated total matches the grand total
        calculated_total = sum(user_final_amounts.values())
        if calculated_total != grand_total:
            discrepancy = round(grand_total - calculated_total, 2)
            return jsonify({
                "error": f"Calculated total {calculated_total} does not match grand total {grand_total}. Discrepancy: {discrepancy}"
            }), 500
        
        return jsonify(final_amounts=user_final_amounts)
    
    except Exception as e:
        return jsonify({"message": "An error occurred while calculating cost", "error": str(e)}), 500


if __name__ == '__main__':
    app.run(debug=True)
