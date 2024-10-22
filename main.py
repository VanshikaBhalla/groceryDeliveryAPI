import razorpay
import jwt
import csv
import os.path
from werkzeug.security import generate_password_hash, check_password_hash
from flask import Flask, request, jsonify
from datetime import datetime, timedelta
import random
import string

app = Flask(__name__)
SECRET_KEY = "hello17World13"

RAZORPAY_KEY_ID = None
RAZORPAY_SECRET_KEY = None
razorpay_client = razorpay.Client(auth=(RAZORPAY_KEY_ID, RAZORPAY_SECRET_KEY))
TXT = "No Delivery Partner Assigned"

USERS_CSV = 'users.csv'
PRODUCTS_CSV = 'products.csv'
CART_CSV = 'cart.csv'
ORDERS_CSV = 'orders.csv'
PAYMENTS_CSV = 'payments.csv'
roles = ["customer", "delivery_personnel"]
categories = ['hygiene', 'beverage', 'snacks', 'electronic', 'fashion']


def generate_product_id():
    characters = string.ascii_uppercase + string.digits
    product_id = ''.join(random.choices(characters, k=5))
    return product_id


def write_to_csv(user_data, filename):
    with open(filename, mode='a', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(user_data)


def read_from_csv(filename):
    if os.path.exists(filename):
        with open(filename, mode='r') as file:
            reader = csv.reader(file)
            users = list(reader)
            return users if users else []
    return []


@app.route('/users/register', methods=['POST'])
def register_user():
    data = request.json
    name = data.get('name')
    email = data.get('email')
    password = data.get('pwd')
    phone = data.get('phone')
    role = data.get('role')  # customer or delivery_personnel

    if not all([name, email, password, phone, role]):
        return jsonify({"error": "All fields are required!"}), 400

    if role not in roles:
        return jsonify({"error": "Invalid role"}), 400
    users = read_from_csv(USERS_CSV)

    for user in users:
        # print(user)
        if user[1] == email or user[3] == phone:
            return jsonify({"error": "user already registered, try using a different email or phn number"}), 400

    hashed_password = generate_password_hash(password)

    user_data = [name, email, hashed_password, phone, role]

    write_to_csv(user_data, USERS_CSV)

    return jsonify({"message": "User registered successfully!"}), 201


def generate_jwt(user_email):
    payload = {
        'email': user_email,
        'exp': datetime.utcnow() + timedelta(hours=24)
    }
    token = jwt.encode(payload, SECRET_KEY, algorithm='HS256')
    return token


@app.route('/users/login', methods=['POST'])
def login_user():
    data = request.json
    email = data.get('email')
    password = data.get('pwd')

    users = read_from_csv(USERS_CSV)

    for user in users:
        if user[1] == email:  # user[1] is the email column
            hashed_password = user[2]  # user[2] is the hashed password column
            if check_password_hash(hashed_password, password):
                token = generate_jwt(email)  # Generate JWT token
                return jsonify({"token": token}), 200
            else:
                return jsonify({"error": "Invalid email or password!"}), 401

    return jsonify({"error": "User not found!"}), 404


@app.route('/users/profile', methods=['GET'])
def fetch_profile():
    data = request.json
    em = data.get('email')

    users = read_from_csv(USERS_CSV)
    user_found = False
    for user in users:
        if user[1] == em:
            user_found = True
            return jsonify({"name": user[0], "email": user[1], "phn": user[3], "role": user[4]}), 200

    if not user_found:
        return jsonify({"error": "No user found by this email"}), 404


@app.route('/users/profile', methods=['PUT'])
def update_profile():   # updating phone number
    data = request.json
    new_phn = data.get('new_phn')
    email = data.get('email')

    if not email or not new_phn:
        return jsonify({"error": "Enter new email & phone number"}), 400

    users = read_from_csv(USERS_CSV)
    updated_users = []
    user_found = False

    for user in users:
        if user[1] == email:
            user[3] = new_phn
            user_found = True
        updated_users.append(user)

    if not user_found:
        return jsonify({"error": "User Not Found!"}), 404

    with open(USERS_CSV, mode='w', newline='') as file:
        writer = csv.writer(file)
        writer.writerows(updated_users)

    return jsonify({"msg": "updated successfully!"}), 200


@app.route('/products', methods=['POST'])
def add_product():
    data = request.json
    pid = generate_product_id()
    pname = data.get('pname')
    price = data.get('price')
    rating = data.get('rating')
    category = data.get('category')
    count = data.get('inStock')
    
    if not all([pname, price, rating, category, count]):
        return jsonify({"error": "All fields are required!"}), 400

    if category not in categories:
        return jsonify({"error": "invalid category"}), 400

    products = read_from_csv(PRODUCTS_CSV)
    pp = []
    for p in products:
        if p[1] == pname:
            for i in products:
                if i[1] == pname:
                    i[5] = int(i[5]) + int(count)
                pp.append(i)
            with open(PRODUCTS_CSV, mode='w', newline='') as file:
                writer = csv.writer(file)
                writer.writerows(pp)
            return jsonify({"error": "product exists in db, thus increasing in stock quantity"}), 400

    pdata = [pid, pname, price, rating, category, count]

    write_to_csv(pdata, PRODUCTS_CSV)

    return jsonify({"message": "Product Added successfully!"}), 201


@app.route('/products/<id_>', methods=['PUT'])
def update_product(id_):   # updating price
    data = request.json
    new_price = data.get('new_price')

    if not new_price:
        return jsonify({"error": "Enter new price"}), 400

    products = read_from_csv(PRODUCTS_CSV)
    updated_products = []
    product_found = False

    for p in products:
        if p[0] == id_:
            product_found = True
            if p[2] != new_price:
                p[2] = new_price
            else:
                return jsonify({"error": "new price same as current price"}), 400
        updated_products.append(p)

    if not product_found:
        return jsonify({"error": "Product Not Found!"}), 404

    with open(PRODUCTS_CSV, mode='w', newline='') as file:
        writer = csv.writer(file)
        writer.writerows(updated_products)

    return jsonify({"msg": "updated successfully!"}), 200


@app.route('/products/count', methods=['PUT'])
def update_product_count():   # updating count
    new_q = request.args.get('new_count')
    id_ = request.args.get('id')
    if not new_q:
        return jsonify({"error": "Enter new quantity"}), 400

    products = read_from_csv(PRODUCTS_CSV)
    updated_products = []
    product_found = False

    for p in products:
        if p[0] == id_:
            product_found = True
            if p[5] != new_q:
                p[5] = new_q
            else:
                return jsonify({"error": "new count same as current count"}), 400
        updated_products.append(p)

    if not product_found:
        return jsonify({"error": "Product Not Found!"}), 404

    with open(PRODUCTS_CSV, mode='w', newline='') as file:
        writer = csv.writer(file)
        writer.writerows(updated_products)

    return jsonify({"msg": "updated successfully!"}), 200


@app.route('/products/<id_>', methods=['DELETE'])
def delete_product(id_):
    products = read_from_csv(PRODUCTS_CSV)
    updated_products = []
    product_found = False

    for p in products:
        if p[0] == id_:
            product_found = True
            continue
        updated_products.append(p)

    if not product_found:
        return jsonify({"error": "Product Not Found!"}), 404

    with open(PRODUCTS_CSV, mode='w', newline='') as file:
        writer = csv.writer(file)
        writer.writerows(updated_products)

    return jsonify({"msg": "deleted successfully!"}), 200


@app.route('/products', methods=['GET'])
def display_products():
    products = read_from_csv(PRODUCTS_CSV)

    if not products:
        return jsonify({"msg": "No products found!"}), 404

    # Group products by category
    grouped_products = {}
    for product in products:
        category = product[4].lower()
        if category not in grouped_products:
            grouped_products[category] = []
        grouped_products[category].append({
            "ProductID": product[0],
            "ProductName": product[1],
            "Price": product[2],
            "Rating": product[3],
            "InStock": product[5]
        })

    return jsonify(grouped_products), 200


@app.route('/products/<id_>', methods=['GET'])
def display_product(id_):
    products = read_from_csv(PRODUCTS_CSV)

    if not products:
        return jsonify({"msg": "No products found!"}), 404

    for product in products:
        if product[0] == id_:
            return jsonify({
            "ProductID": product[0],
            "ProductName": product[1],
            "Price": product[2],
            "Rating": product[3],
            "Category": product[4],
            "InStock": product[5]}), 200


@app.route('/products/search', methods=['GET'])
def search_product():
    q = request.args.get('key', '').lower()

    if not q:
        return jsonify({"error": "query parameter needed!"}), 400

    products = read_from_csv(PRODUCTS_CSV)

    if not products:
        return jsonify({"msg": "No products found!"}), 404

    res = []

    for p in products:
        p_name = p[1].lower()
        p_cat = p[4].lower()
        if q in p_name or q in p_cat:
            res.append({
                "Product ID": p[0],
                "Product Name": p[1],
                "Price": p[2],
                "Rating": p[3],
                "Category": p[4],
                "In Stock": p[5]
            })

    if not res:
        return jsonify({"msg": "No products found!"}), 404

    return jsonify(res), 200


@app.route('/cart/add', methods=['POST'])
def add_to_cart():
    data = request.json
    user_email = data.get('email')
    product_id = data.get('product_id')
    quantity = data.get('quantity')

    if not all([user_email, product_id, quantity]):
        return jsonify({"error": "User email, product ID, and quantity are required!"}), 400

    users = read_from_csv(USERS_CSV)
    user_found = False
    for user in users:
        if user[1] == user_email:
            user_found = True
            break
    if not user_found:
        return jsonify({"error": "User not found!"}), 400

    products = read_from_csv(PRODUCTS_CSV)
    product_found = False
    for product in products:
        if product[0] == product_id:
            product_found = True
            break
    if not product_found:
        return jsonify({"error": "Product not found!"}), 404

    cart_items = read_from_csv(CART_CSV)
    updated_cart = []
    item_exists = False

    for item in cart_items:
        if item[0] == user_email and item[1] == product_id:
            item[2] = str(int(item[2]) + int(quantity))  # Update quantity if already in cart
            item_exists = True
        updated_cart.append(item)

    if not item_exists:
        cart_item = [user_email, product_id, quantity]
        updated_cart.append(cart_item)

    with open(CART_CSV, mode='w', newline='') as file:
        writer = csv.writer(file)
        writer.writerows(updated_cart)

    return jsonify({"message": "Item added to cart successfully!"}), 201


@app.route('/cart', methods=['GET'])
def get_cart():
    user_found = False
    id_ = request.args.get('email')
    users = read_from_csv(USERS_CSV)
    for user in users:
        if id_ == user[1]:
            user_found = True
            break
    if not user_found:
        return jsonify({"error": "User not found!"}), 400

    cart = read_from_csv(CART_CSV)
    user_found = False
    order = []
    for i in cart:
        if i[0] == id_:
            user_found = True
            order.append((i[1], i[2]))

    if not user_found:
        return jsonify({"msg": "Empty Cart"}), 400

    res = []
    products = read_from_csv(PRODUCTS_CSV)
    for x in order:
        for p in products:
            if x[0] == p[0]:
                res.append({
                    "Product ID": p[0],
                    "Product Name": p[1],
                    "Product Price (per unit)": p[2],
                    "In cart": x[1],
                    "In Stock": p[5]
                })
    return jsonify(res), 200


@app.route('/cart/<product_id>', methods=['DELETE'])
def remove_from_cart(product_id):
    user_email = request.args.get('email')

    if not user_email:
        return jsonify({"error": "User email is required!"}), 400

    cart_items = read_from_csv('cart.csv')
    updated_cart = []
    product_found = False

    for item in cart_items:
        if item[0] == user_email and item[1] == product_id:
            product_found = True
            continue  # Skip the product to be removed
        updated_cart.append(item)

    if not product_found:
        return jsonify({"error": "Product not found in the cart!"}), 404

    with open('cart.csv', mode='w', newline='') as file:
        writer = csv.writer(file)
        writer.writerows(updated_cart)

    return jsonify({"message": "Product deleted from cart successfully!"}), 200


@app.route('/orders/checkout', methods=['POST'])
def place_order():
    email = request.args.get('email')

    if not email:
        return jsonify({"error": "User email is required!"}), 400

    cart = read_from_csv('cart.csv')
    products = read_from_csv(PRODUCTS_CSV)
    user_cart = [item for item in cart if item[0] == email]

    if not user_cart:
        return jsonify({"error": "Empty Cart"}), 400

    order_id = ''.join(random.choices(string.ascii_uppercase + string.digits, k=8))
    total_price = 0
    order_items = []

    for cart_item in user_cart:
        product_id = cart_item[1]
        quantity = int(cart_item[2])
        for product in products:
            if product[0] == product_id:
                if int(product[5]) < quantity:
                    return jsonify({"error": "some items are out of stock"})

                price = float(product[2])
                total_price += price * quantity
                order_items.append([order_id, email, product_id, quantity, price * quantity])
                break

    delivery_status = "Processing"
    estimated_delivery_time = (datetime.now() + timedelta(days=5)).strftime("%Y-%m-%d")

    for order_item in order_items:
        order_item.append(delivery_status)
        order_item.append(estimated_delivery_time)
        order_item.append(TXT)
        order_item.append("None")
        write_to_csv(order_item, ORDERS_CSV)

    updated_cart = [item for item in cart if item[0] != email]
    with open('cart.csv', mode='w', newline='') as file:
        writer = csv.writer(file)
        writer.writerows(updated_cart)

    return jsonify({
        "message": "Order placed successfully!",
        "OrderID": order_id,
        "TotalPrice": total_price,
        "EstimatedDeliveryTime": estimated_delivery_time,
        "AssignedDeliveryPartner": TXT
    }), 201


@app.route('/orders/<order_id>', methods=['GET'])
def get_order_details(order_id):
    email = request.args.get('email')

    if not email:
        return jsonify({"error": "User email is required!"}), 400

    orders = read_from_csv(ORDERS_CSV)
    order_details = [order for order in orders if order[0] == order_id and order[1] == email]

    if not order_details:
        return jsonify({"error": "Order not found!"}), 404

    order_info = {
        "OrderID": order_id,
        "Items": [],
        "TotalPrice": 0,
        "PaymentStatus": order_details[0][5],
        "EstimatedDeliveryTime": order_details[0][6],
        "AssignedDeliveryPartner": order_details[0][7],
        "DeliveredStatus": order_details[0][8]
    }

    total_price = 0
    for order in order_details:
        order_info["Items"].append({
            "ProductID": order[2],
            "Quantity": order[3],
            "Price": order[4]
        })
        total_price += float(order[4])

    order_info["TotalPrice"] = total_price

    return jsonify(order_info), 200


@app.route('/payments/init', methods=['POST'])
def init_payment():
    order_id = request.args.get('order_id')
    email = request.args.get('email')

    if not order_id or not email:
        return jsonify({"error": "Order ID and user email are required!"}), 400

    orders_ = read_from_csv(ORDERS_CSV)
    order_ = [o for o in orders_ if o[0] == order_id and o[1] == email]
    if not order_:
        return jsonify({"error": "Order not found!"}), 404

    updated_orders = []
    for o in orders_:
        if o[0] == order_id and o[1] == email:
            o[5] = "Payment Initiated"
        updated_orders.append(o)

    with open(ORDERS_CSV, mode='w', newline='') as file:
        writer = csv.writer(file)
        writer.writerows(updated_orders)

    # total_price = sum(float(o[4]) for o in order_) * 100  # razorpay accepts payments in paise
    # payment_order = razorpay_client.order.create({
    #     "amount": total_price,
    #     "currency": "INR",
    #     "receipt": f"receipt_{order_id}",
    #     "payment_capture": 1
    # })
    #
    # payment_data = [payment_order['id'], order_id, email, total_price / 100, "Pending"]
    # write_to_csv(payment_data, PAYMENTS_CSV)
    #
    # return jsonify({
    #     "msg": "Payment Successful!",
    #     "payment_id": payment_order['id'],
    #     "amount": total_price/100
    # }), 201

    # ----------------mock implementation of payment since razorpay need 3-4 business days for verification------------------

    total_price = sum(float(o[4]) for o in order_)

    payment_token = ''.join(random.choices(string.ascii_uppercase + string.digits, k=10))
    payment_link = f"https://mockpaymentgateway.com/pay/{payment_token}"
    payment_data = [payment_token, order_id, email, total_price, "Pending"]
    write_to_csv(payment_data, PAYMENTS_CSV)

    return jsonify({
        "message": "Payment initiated successfully!",
        "payment_link": payment_link,
        "amount": total_price
    }), 201


@app.route('/payments/verify', methods=['POST'])
def verify_payment():
    # payment_id = request.args.get('payment_id')
    # razorpay_order_id = request.args.get('order_id')
    # razorpay_signature = request.args.get('signature')
    #
    # if not all([payment_id, razorpay_order_id, razorpay_signature]):
    #     return jsonify({"error": "Missing payment details!"}), 400
    #
    # try:
    #     razorpay_client.utility.verify_payment_signature({
    #         'razorpay_order_id': razorpay_order_id,
    #         'razorpay_payment_id': payment_id,
    #         'razorpay_signature': razorpay_signature
    #     })
    # except razorpay.errors.SignatureVerificationError:
    #     return jsonify({"error": "Payment verification failed!"}), 400
    #
    # payments = read_from_csv(PAYMENTS_CSV)
    # updated_payments = []
    # payment_found = False
    # p_id = None
    #
    # for payment in payments:
    #     if payment[0] == razorpay_order_id:
    #         p_id = payment[1]
    #         payment_found = True
    #         payment[4] = "Success"
    #     updated_payments.append(payment)
    #
    # if not payment_found:
    #     return jsonify({"error": "Payment not found!"}), 404
    #
    # with open(PAYMENTS_CSV, mode='w', newline='') as file:
    #     writer = csv.writer(file)
    #     writer.writerows(updated_payments)
    #
    # orders = read_from_csv(ORDERS_CSV)
    # updated_orders = []
    # for order in orders:
    #     if order[0] == payment[1]:
    #         order[5] = "Paid"
    #     updated_orders.append(order)
    #
    # with open('orders.csv', mode='w', newline='') as file:
    #     writer = csv.writer(file)
    #     writer.writerows(updated_orders)
    #
    # return jsonify({"message": "Payment verified successfully!"}), 200

    # ----------------mock implementation of payment since razorpay need 3-4 business days for verification------------------

    payment_token = request.args.get('payment_token')
    payment_status = request.args.get('status').lower()
    email = request.args.get('email')

    if not all([payment_token, payment_status, email]):
        return jsonify({"error": "Payment token, status, and user email are required!"}), 400

    payments = read_from_csv(PAYMENTS_CSV)
    payment_found = False
    updated_payments = []
    p_id = None

    for p in payments:
        if p[0] == payment_token and p[2] == email:
            payment_found = True
            p_id = p[1]
            p[4] = payment_status
        updated_payments.append(p)

    if not payment_found:
        return jsonify({"error": "Payment not found!"}), 404

    with open(PAYMENTS_CSV, mode='w', newline='') as file:
        writer = csv.writer(file)
        writer.writerows(updated_payments)

    if payment_status == "success":
        orders = read_from_csv(ORDERS_CSV)
        updated_orders = []
        for order in orders:
            if order[0] == p_id:
                order[5] = "Paid"
            updated_orders.append(order)

        with open(ORDERS_CSV, mode='w', newline='') as file:
            writer = csv.writer(file)
            writer.writerows(updated_orders)

    return jsonify({"message": f"Payment verification: {payment_status}!"}), 200


@app.route('/payments/history', methods=['GET'])
def payment_history():
    email = request.args.get('email')
    if not email:
        return jsonify({"error": "Email is required!"}), 400

    users = read_from_csv(USERS_CSV)
    user_exists = any(u[1] == email for u in users)
    if not user_exists:
        return jsonify({"message": "No user found"}), 404

    payments = read_from_csv(PAYMENTS_CSV)
    p_history = [p for p in payments if p[2] == email]
    if not p_history:
        return jsonify({"message": "No payment history found for this user"}), 404

    return jsonify({"payment_history": p_history}), 200


@app.route('/orders/<order_id>/track', methods=['GET'])
def track_order(order_id):
    orders = read_from_csv(ORDERS_CSV)

    for order in orders:
        if order[0] == order_id:
            return jsonify({
                "OrderID": order[0],
                "Status": order[5]
            }), 200

    return jsonify({"error": "Order not found!"}), 404


@app.route('/orders/<order_id>/assign', methods=['POST'])
def assign_delivery_partner(order_id):
    delivery_personnel_email = request.args.get('email')

    if not delivery_personnel_email:
        return jsonify({"error": "Delivery personnel email is required!"}), 400

    users = read_from_csv(USERS_CSV)
    delivery_found = False
    for user in users:
        if user[1] == delivery_personnel_email and user[4] == 'delivery_personnel':  # Check delivery personnel role
            delivery_found = True
            break

    if not delivery_found:
        return jsonify({"error": "Invalid delivery personnel email."}), 400

    orders = read_from_csv(ORDERS_CSV)
    updated_orders = []
    order_found = False

    for order in orders:
        if order[0] == order_id:
            order_found = True
            order[7] = delivery_personnel_email
        updated_orders.append(order)

    if not order_found:
        return jsonify({"error": "Order not found!"}), 404

    with open(ORDERS_CSV, mode='w', newline='') as file:
        writer = csv.writer(file)
        writer.writerows(updated_orders)

    return jsonify({"message": "Delivery partner assigned successfully!"}), 200


@app.route('/delivery/update-status', methods=['POST'])
def update_delivery_status():
    data = request.json
    order_id = data.get('order_id')
    delivery_personnel_email = data.get('delivery_personnel_email')
    new_status = data.get('status')  # New status to update (e.g., "Picked Up," "On the Way," "Delivered")

    if not order_id or not delivery_personnel_email or not new_status:
        return jsonify({"error": "Order ID, delivery personnel email, and status are required!"}), 400

    users = read_from_csv(USERS_CSV)
    delivery_found = False
    for user in users:
        if user[1] == delivery_personnel_email and user[4] == 'delivery_personnel':
            delivery_found = True
            break

    if not delivery_found:
        return jsonify({"error": "Invalid delivery personnel email."}), 400

    orders = read_from_csv(ORDERS_CSV)
    updated_orders = []
    order_found = False
    for order in orders:
        if order[0] == order_id:
            order_found = True
            if order[7] != delivery_personnel_email:
                return jsonify({"error": "You are not assigned to this order!"}), 403

            order[8] = new_status
        updated_orders.append(order)

    if not order_found:
        return jsonify({"error": "Order not found!"}), 404

    with open(ORDERS_CSV, mode='w', newline='') as file:
        writer = csv.writer(file)
        writer.writerows(updated_orders)

    return jsonify({"message": "Order status updated successfully!"}), 200


@app.route('/admin/dashboard', methods=['GET'])
def admin_dashboard():
    orders = read_from_csv(ORDERS_CSV)
    users = read_from_csv(USERS_CSV)
    products = read_from_csv(PRODUCTS_CSV)

    total_orders = len(orders)

    active_users = len([user for user in users if user[4] != 'delivery_personnel'])

    product_sales = {}
    for order in orders:
        product_id = order[2]
        quantity = int(order[3])
        if product_id in product_sales:
            product_sales[product_id] += quantity
        else:
            product_sales[product_id] = quantity

    top_selling_products = sorted(product_sales.items(), key=lambda x: x[1], reverse=True)[:3]
    top_selling_product_names = [get_product_name(product_id) for product_id, _ in top_selling_products]

    total_delivery_time = 0
    delivery_count = 0
    for order in orders:
        if order[8] == 'Delivered':
            delivery_time = datetime.strptime(order[6], "%Y-%m-%d")
            pickup_time = datetime.now()
            total_delivery_time += (delivery_time - pickup_time).total_seconds() / 3600
            delivery_count += 1

    avg_delivery_time = total_delivery_time / delivery_count if delivery_count > 0 else 0

    dashboard_stats = {
        "total_orders": total_orders,
        "active_users": active_users,
        "top_selling_products": top_selling_product_names,
        "average_delivery_time_hours": round(avg_delivery_time, 2)
    }

    return jsonify(dashboard_stats), 200


def get_product_name(product_id):
    products = read_from_csv(PRODUCTS_CSV)
    for product in products:
        if product[0] == product_id:
            return product[1]
    return "Unknown Product"


@app.route('/admin/orders', methods=['GET'])
def fetch_orders():
    status = request.args.get('status')  # optional
    orders = read_from_csv(ORDERS_CSV)

    if status:
        filtered_orders = [order for order in orders if order[5] == status or order[8]==status]
        return jsonify(filtered_orders), 200

    return jsonify(orders), 200


@app.route('/admin/orders/<order_id>/cancel', methods=['PUT'])
def cancel_order(order_id):
    orders = read_from_csv(ORDERS_CSV)
    updated_orders = []
    order_found = False

    for order in orders:
        if order[0] == order_id:
            order_found = True
            if order[8] == 'Delivered':
                return jsonify({'error': "order already delivered, can't cancel"}), 400
            order[5] = 'canceled'
        updated_orders.append(order)

    if not order_found:
        return jsonify({"error": "Order Not Found!"}), 404

    with open(ORDERS_CSV, mode='w', newline='') as file:
        writer = csv.writer(file)
        writer.writerows(updated_orders)

    return jsonify({"msg": "Order canceled successfully!"}), 200


if __name__ == "__main__":
    app.run(debug=True)
