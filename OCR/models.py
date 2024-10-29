from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash

db = SQLAlchemy()

class User(db.Model):
    __tablename__ = 'users'
    user_id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    password = db.Column(db.String(255), nullable=False)
    phone_number = db.Column(db.String(15))

    # Relationships
    receipts = db.relationship('Receipt', backref='uploader', lazy=True)
    selections = db.relationship('UserItemSelection', backref='user', lazy=True)

    def set_password(self, password):
        self.password = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password, password)

#lists general receipt info but the items are listed in ReceiptItem
class Receipt(db.Model):
    __tablename__ = 'receipts'
    receipt_id = db.Column(db.Integer, primary_key=True)
    uploaded_by = db.Column(db.Integer, db.ForeignKey('users.user_id'), nullable=False)
    receipt_image_name = db.Column(db.String(255), unique=True, nullable=False)  # Name of the uploaded image
    #image_path = db.Column(db.Text, nullable=False)
    date = db.Column(db.DateTime, default=db.func.current_timestamp())
    vendor_name=db.Column(db.String(255), nullable=False)
    vendor_address=db.Column(db.String(255), nullable=True)
    purchase_time=db.Column(db.DateTime, nullable=True)
    subtotal = db.Column(db.Numeric(10, 2))
    tax = db.Column(db.Numeric(10, 2))
    grand_total = db.Column(db.Numeric(10, 2))
    #if all items in list have been claimed
    completed=db.Column(db.Boolean, default=False, nullable=False)

    # Relationships
    items = db.relationship('ReceiptItem', backref='receipt', lazy=True, cascade="all, delete")
    participants = db.relationship('ReceiptParticipant', backref='receipt', lazy=True, cascade="all, delete")

#connects each unique item to receipt 
class ReceiptItem(db.Model):
    __tablename__ = 'receipt_items'
    item_id = db.Column(db.Integer, primary_key=True)
    receipt_id = db.Column(db.Integer, db.ForeignKey('receipts.receipt_id'), nullable=False)
    description = db.Column(db.String(255), nullable=False)
    price = db.Column(db.Numeric(10, 2), nullable=False)

    # Relationships
    selections = db.relationship('UserItemSelection', backref='item', lazy=True, cascade="all, delete")


#who is invited to collab on receipt
class ReceiptParticipant(db.Model):
    __tablename__ = 'receipt_participants'
    id = db.Column(db.Integer, primary_key=True)
    receipt_id = db.Column(db.Integer, db.ForeignKey('receipts.receipt_id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.user_id'), nullable=False)

    # Ensure unique pairing of receipt and user
    __table_args__ = (db.UniqueConstraint('receipt_id', 'user_id', name='_receipt_user_uc'),)

#associate user with item they selected
class UserItemSelection(db.Model):
    __tablename__ = 'user_item_selections'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.user_id'), nullable=False)
    item_id = db.Column(db.Integer, db.ForeignKey('receipt_items.item_id'), nullable=False)
    receipt_id=db.Column(db.Integer, db.ForeignKey('receipts.receipt_id'), nullable=False)

    # Ensure unique selection of each item by each user
    __table_args__ = (db.UniqueConstraint('user_id', 'item_id', name='_user_item_uc'),)
