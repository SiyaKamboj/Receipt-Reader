import json
from flask import Flask, jsonify, request
#from runmodel import passToApi
from flask_cors import CORS
import requests
import base64
from flask_sqlalchemy import SQLAlchemy
import os
from models import Receipt, ReceiptItem, User, db

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
    # Assuming receipt_image is sent in the POST request
    if 'receipt_image' in request.files:
        receipt_image = request.files['receipt_image']
        receipt_image_name = receipt_image.filename

        # Check if receipt already exists in the database
        existing_receipt = Receipt.query.filter_by(receipt_image_name=receipt_image_name).first()
        #existing_receipt=True
        if existing_receipt:
            #get receipt id so u can query items table
            receipt_id=existing_receipt.receipt_id
            #get all items with certain receipt id
            items=ReceiptItem.query.filter_by(receipt_id=receipt_id).all()
            #TODO DONE : change this to query line items in the other table
            return jsonify({
                "line_items": items,
                "subtotal": existing_receipt.subtotal,
                "tax": existing_receipt.tax,
                "grandtotal": existing_receipt.grandtotal
            })


        try:
            #TODO : add in line items into separate table as well
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

            # Store the result in the database
            #TODO: upload user_id into here, remove line_items
            new_receipt = Receipt(
                receipt_image_name=receipt_image_name,
                line_items=line_items,
                subtotal=subtotal,
                tax=tax,
                grandtotal=grandtotal
            )
            db.session.add(new_receipt)
            db.session.commit()

            #for debugging purposes
            for item in line_items:
                description = item.get("description")
                total = item.get("total")
                print(f"Item: {description}, \tCost: ${total:.2f}")
            print(f"Subtotal: ${subtotal:.2f}")
            print(f"Tax: ${tax:.2f}")
            print(f"Grand Total: ${grandtotal:.2f}")

            # simplified_response = {
            #     "line_items": line_items,
            #     "subtotal": subtotal,
            #     "tax": tax,
            #     "grandtotal": grandtotal
            # }

            # return jsonify(simplified_response)

            #TODO : update the jsonify
            return jsonify({
                "line_items": line_items,
                "subtotal": subtotal,
                "tax": tax,
                "grandtotal": grandtotal
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
    #return jsonify({"message": "User registered successfully."}), 201
    return 201

@app.route('/api/login', methods=['POST'])
def login():
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')

    user = User.query.filter_by(username=username).first()
    if user and user.check_password(password):
        return jsonify({"message": "Login successful."}), 200
    return jsonify({"error": "Invalid username or password."}), 401


if __name__ == '__main__':
    app.run(debug=True)
