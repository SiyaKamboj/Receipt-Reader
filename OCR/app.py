import json
from flask import Flask, jsonify, request
#from runmodel import passToApi
from flask_cors import CORS
import requests
import base64
from flask_sqlalchemy import SQLAlchemy
import os
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
CORS(app)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///receipts.db'  # Using SQLite for simplicity
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

#creates a table called receipt and stores each receipt, ensuring that unique ones are not re-added
class Receipt(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    receipt_image_name = db.Column(db.String(255), unique=True, nullable=False)  # Name of the uploaded image
    line_items = db.Column(db.JSON)  # Store line items as JSON
    subtotal = db.Column(db.Float)
    tax = db.Column(db.Float)
    grandtotal = db.Column(db.Float)

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(150), unique=True, nullable=False)
    email = db.Column(db.String(150), unique=True, nullable=False)
    password = db.Column(db.String(150), nullable=False)
    phone_number = db.Column(db.String(15), nullable=True)

    def set_password(self, password):
        self.password = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password, password)

with app.app_context():
    db.create_all() # Creates tables if they don't exist

def getItemizedData():
    # Load itemized data from a local JSON file for testing
    with open("response1.json", "r") as f:
        data = json.load(f)
    items = data['receipts'][0]['items']
    return items

clientKey = os.getenv('clientKey')
authorization= os.getenv('authorization')

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
            return jsonify({
                "line_items": existing_receipt.line_items,
                "subtotal": existing_receipt.subtotal,
                "tax": existing_receipt.tax,
                "grandtotal": existing_receipt.grandtotal
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
                'CLIENT-ID': clientKey,
                'AUTHORIZATION': authorization
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
    phone_number = data.get('phone_number')

    if User.query.filter_by(username=username).first():
        return jsonify({"error": "Username already exists."}), 400

    new_user = User(username=username, email=email)
    new_user.set_password(password)
    new_user.phone_number = phone_number
    db.session.add(new_user)
    db.session.commit()
    return jsonify({"message": "User registered successfully."}), 201

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
