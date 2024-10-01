from flask import Flask, jsonify, request
from flask_sqlalchemy import SQLAlchemy
from flask_marshmallow import Marshmallow
from marshmallow import fields, ValidationError
import datetime

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+mysqlconnector://root:password@127.0.0.1/e_commerce_db'
db = SQLAlchemy(app)
ma = Marshmallow(app)

class CustomerSchema(ma.SQLAlchemyAutoSchema):
    name = fields.String(required=True)
    email = fields.String()
    phone = fields.String()

    class Meta:
        model = 'Customer'
        fields = ('id', 'name', 'email', 'phone')

customer_schema = CustomerSchema()
customers_schema = CustomerSchema(many=True)

class ProductSchema(ma.SQLAlchemyAutoSchema):
    name = fields.String(required=True)
    price = fields.Float(required=True)
    stock = fields.Int()

    class Meta:
        model = 'Product'
        fields = ('id', 'name', 'price', 'stock')

product_schema = ProductSchema()
products_schema = ProductSchema(many=True)

class CustomerAccountSchema(ma.SQLAlchemyAutoSchema):
    username = fields.String(required=True)
    password = fields.String(required=True)
    customer_id = fields.Int()

    class Meta:
        model = 'CustomerAccount'
        fields = ('id', 'username', 'password', 'customer_id')

customer_account_schema = CustomerAccountSchema()
customer_accounts_schema = CustomerAccountSchema(many=True)

class Customer(db.Model):
    __tablename__ = 'Customers'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), nullable=False)
    email = db.Column(db.String(320))
    phone = db.Column(db.String(15))
    orders = db.relationship('Order', backref='customer')

class Product(db.Model):
    __tablename__ = 'Products'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), nullable=False)
    price = db.Column(db.Float, nullable=False)
    stock = db.Column(db.Integer, default=0)  # Added stock field
    orders = db.relationship('Order', secondary='order_product', backref=db.backref('products'))

class Order(db.Model):
    __tablename__ = 'Orders'
    id = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.Date, nullable=False)
    customer_id = db.Column(db.Integer, db.ForeignKey('Customers.id'))

class CustomerAccount(db.Model):
    __tablename__ = 'Customer_Accounts'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(255), unique=True, nullable=False)
    password = db.Column(db.String(255), nullable=False)
    customer_id = db.Column(db.Integer, db.ForeignKey('Customers.id'))
    customer = db.relationship('Customer', backref='customer_account', uselist=False)

order_product = db.Table('Order_Product',
    db.Column('order_id', db.Integer, db.ForeignKey('Orders.id'), primary_key=True),
    db.Column('product_id', db.Integer, db.ForeignKey('Products.id'), primary_key=True)
)

RESTOCK_THRESHOLD = 10  
RESTOCK_AMOUNT = 50     

@app.route('/customer_accounts', methods=['POST'])
def add_customer_account():
    try:
        account_data = customer_account_schema.load(request.json)
    except ValidationError as err:
        return jsonify(err.messages), 400
    
    new_account = CustomerAccount(
        username=account_data['username'],
        password=account_data['password'],  
        customer_id=account_data['customer_id']
    )
    db.session.add(new_account)
    db.session.commit()
    return jsonify({"message": "New customer account added successfully"}), 201

@app.route('/customer_accounts/<int:id>', methods=['PUT'])
def update_customer_account(id):
    account = CustomerAccount.query.get_or_404(id)
    try:
        account_data = customer_account_schema.load(request.json)
    except ValidationError as err:
        return jsonify(err.messages), 400
    
    account.username = account_data['username']
    account.password = account_data['password']  
    db.session.commit()
    return jsonify({"message": "Customer account updated successfully"}), 200

@app.route('/customer_accounts/<int:id>', methods=['DELETE'])
def delete_customer_account(id):
    account = CustomerAccount.query.get_or_404(id)
    db.session.delete(account)
    db.session.commit()
    return jsonify({"message": "Customer account deleted successfully"}), 200

@app.route('/customer_accounts', methods=['GET'])
def get_customer_accounts():
    accounts = CustomerAccount.query.all()
    return customer_accounts_schema.jsonify(accounts)

@app.route('/customers', methods=['GET'])
def get_customers():
    customers = Customer.query.all()
    return customers_schema.jsonify(customers)

@app.route('/customers', methods=['POST'])
def add_customer():
    try:
        customer_data = customer_schema.load(request.json)
    except ValidationError as err:
        return jsonify(err.messages), 400
    
    new_customer = Customer(
        name=customer_data['name'],
        email=customer_data['email'],
        phone=customer_data['phone']
    )
    db.session.add(new_customer)
    db.session.commit()
    return jsonify({"message": "New customer added successfully"}), 201

@app.route('/customers/<int:id>', methods=['PUT'])
def update_customer(id):
    customer = Customer.query.get_or_404(id)
    try:
        customer_data = customer_schema.load(request.json)
    except ValidationError as err:
        return jsonify(err.messages), 400
    
    customer.name = customer_data['name']
    customer.email = customer_data['email']
    customer.phone = customer_data['phone']
    db.session.commit()
    return jsonify({"message": "Customer details updated successfully"}), 200

@app.route('/customers/<int:id>', methods=['DELETE'])
def delete_customer(id):
    customer = Customer.query.get_or_404(id)
    db.session.delete(customer)
    db.session.commit()
    return jsonify({"message": "Customer removed successfully"}), 200

@app.route('/products', methods=['POST'])
def add_product():
    try:
        product_data = product_schema.load(request.json)
    except ValidationError as err:
        return jsonify(err.messages), 400
    
    new_product = Product(name=product_data['name'], price=product_data['price'])
    db.session.add(new_product)
    db.session.commit()
    return jsonify({"message": "New product added successfully"}), 201

@app.route('/products/<int:id>', methods=['PUT'])
def update_product(id):
    product = Product.query.get_or_404(id)
    try:
        product_data = product_schema.load(request.json)
    except ValidationError as err:
        return jsonify(err.messages), 400
    
    product.name = product_data['name']
    product.price = product_data['price']
    db.session.commit()
    return jsonify({"message": "Product updated successfully"}), 200

@app.route('/products/<int:id>', methods=['DELETE'])
def delete_product(id):
    product = Product.query.get_or_404(id)
    db.session.delete(product)
    db.session.commit()
    return jsonify({"message": "Product deleted successfully"}), 200

@app.route('/products', methods=['GET'])
def get_products():
    products = Product.query.all()
    return products_schema.jsonify(products)

@app.route('/products/<int:id>', methods=['GET'])
def get_product(id):
    product = Product.query.get_or_404(id)
    return product_schema.jsonify(product)

@app.route('/products/<int:id>/stock', methods=['GET'])
def get_product_stock(id):
    product = Product.query.get_or_404(id)
    return jsonify({'id': product.id, 'name': product.name, 'stock': product.stock})

@app.route('/products/<int:id>/stock', methods=['PUT'])
def update_product_stock(id):
    product = Product.query.get_or_404(id)
    stock_data = request.json.get('stock')

    if stock_data is not None:
        product.stock = stock_data
        db.session.commit()
        return jsonify({"message": "Stock updated successfully"}), 200
    
    return jsonify({"error": "Stock value is required"}), 400

@app.route('/orders', methods=['POST'])
def place_order():
    order_data = request.json
    customer_id = order_data.get('customer_id')
    product_ids = order_data.get('product_ids', [])
    
    new_order = Order(customer_id=customer_id, date=datetime.date.today())
    db.session.add(new_order)
    
    for product_id in product_ids:
        product = Product.query.get_or_404(product_id)
        if product.stock <= 0:
            return jsonify({"error": f"Product {product_id} is out of stock."}), 400
        
        new_order.products.append(product)
        product.stock -= 1  

    db.session.commit()
    return jsonify({"message": "Order placed successfully", "order_id": new_order.id}), 201

@app.route('/orders/<int:id>', methods=['GET'])
def get_order(id):
    order = Order.query.get_or_404(id)
    return jsonify({
        'id': order.id,
        'customer_id': order.customer_id,
        'date': order.date.isoformat(),
        'products': [product.id for product in order.products]
    })

@app.route('/products/restock', methods=['POST'])
def restock_products():
    products_to_restock = request.json.get('products', [])
    
    for product_id in products_to_restock:
        product = Product.query.get_or_404(product_id)
        product.stock += RESTOCK_AMOUNT
    
    db.session.commit()
    return jsonify({"message": "Products restocked successfully"}), 200

if __name__ == '__main__':
    app.run(debug=True)