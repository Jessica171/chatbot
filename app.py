from flask import Flask, jsonify, request, session

# from chatbot import entery
from flask_session import Session
from flask_cors import CORS
import re
import mysql.connector
from datetime import datetime
import base64
from nlp import entry

app = Flask(__name__)
CORS(app)

# Configure session to use filesystem (for demonstration purposes)
app.config['SESSION_TYPE'] = 'filesystem'
app.config['SECRET_KEY'] = 'your_secret_key'

# Initialize session
Session(app)

# Connect to MySQL database
mydb = mysql.connector.connect(
    host='localhost',
    user='root',
    password='Jessy92100#*',
    port='3306',
    database='convocart'
)




@app.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    email = data.get('email')
    password = data.get('password')

    # Create cursor
    mycursor = mydb.cursor()

    # Prepare SQL query to fetch user's password based on email
    sql = "SELECT iduser, password FROM user WHERE email = %s"
    val = (email,)

    # Execute SQL query
    mycursor.execute(sql, val)

    # Fetch one record
    result = mycursor.fetchone()

    if result and result[1] == password:
        # Store user id in session
        session['user_id'] = result[0]
        return jsonify({'message': 'Login successful'})
    else:
        return jsonify({'message': 'Invalid email or password'}), 401
@app.route('/signup', methods=['POST'])
def signup():
    data = request.get_json()
    fullname = data.get('fullname')
    email = data.get('email')
    phone_number = data.get('phone_number')
    password = data.get('password')
    confirm_password = data.get('confirm_password')

    # Email validation
    if not re.match(r"[^@]+@[^@]+\.[^@]+", email):
        return jsonify({'message': 'Invalid email format'}), 40

    # Phone number validation
    if not re.match(r"^01[0-9]{9}$", phone_number):
        return jsonify({'message': 'Invalid phone number format'}), 4001

    # Password validation
    if not any(char.isupper() for char in password):
        return jsonify({'message': 'Password must contain at least one capital letter'}), 700

        # Check if passwords match
    if password != confirm_password:
        return jsonify({'message': 'Passwords do not match'}), 500

    # Create cursor
    mycursor = mydb.cursor()

    # Check if email already exists
    sql = "SELECT iduser FROM user WHERE email = %s"
    val = (email,)
    mycursor.execute(sql, val)
    result = mycursor.fetchone()
    if result:
        return jsonify({'message': 'Email already exists'}), 2

    # Insert new user into the database
    sql = "INSERT INTO user (username, email, phonenumber, password) VALUES (%s, %s, %s, %s)"
    val = (fullname, email, phone_number, password)
    mycursor.execute(sql, val)
    mydb.commit()

    return jsonify({'message': 'Signup successful'}), 201


@app.route('/reset_password', methods=['POST'])
def reset_password():
    data = request.get_json()
    email = data.get('email')
    new_password = data.get('password')

    # Create cursor
    mycursor = mydb.cursor()

    # Check if email exists in the database
    sql = "SELECT iduser FROM user WHERE email = %s"
    val = (email,)
    mycursor.execute(sql, val)
    result = mycursor.fetchone()

    if result:
        # Update user's password with the new password
        sql = "UPDATE user SET password = %s WHERE email = %s"
        val = (new_password, email)
        mycursor.execute(sql, val)
        mydb.commit()

        return jsonify({'message': 'Password reset successful'}), 200
    else:
        return jsonify({'message': 'Email not found'}), 404


@app.route('/logout', methods=['POST'])
def logout():
    # Remove user id from session
    session.pop('user_id', None)
    return jsonify({'message': 'Logout successful'})


@app.route('/products', methods=['GET'])
def list_products():
    # Create cursor
    mycursor = mydb.cursor(dictionary=True)

    # Fetch all products from the database
    mycursor.execute("SELECT idcloth, name, price,brand FROM cloth_bc")
    products = mycursor.fetchall()

    return jsonify(products)

@app.route('/products/<int:product_id>', methods=['GET'])
def get_product_details(product_id):
    # Create cursor
    mycursor = mydb.cursor(dictionary=True)

    # Fetch product details from the database based on the product_id
    sql = "SELECT name,color,size,price,description,brand,category,gender FROM cloth_bc WHERE idcloth = %s"
    val = (product_id,)
    mycursor.execute(sql, val)
    product = mycursor.fetchone()

    if product:
        return jsonify(product), 200
    else:
        return jsonify({'message': 'Product not found'}), 404

@app.route('/search', methods=['GET'])
def search_products():
    # Get the search query from the request parameters
    search_query = request.args.get('q')

    if not search_query:
        return jsonify({'message': 'No search query provided'}), 400

    # Create cursor
    mycursor = mydb.cursor(dictionary=True)

    # Construct the SQL query to search for products
    sql = "SELECT idcloth, name, description, price FROM cloth WHERE name LIKE %s OR description LIKE %s"
    val = ("%" + search_query + "%", "%" + search_query + "%")

    # Execute the SQL query
    mycursor.execute(sql, val)
    search_results = mycursor.fetchall()

    return jsonify(search_results)


@app.route('/add_to_cart', methods=['POST'])
def add_to_cart():
    if 'user_id' not in session:
        return jsonify({'message': 'User not logged in'}), 401

    data = request.get_json()
    product_id = data.get('idcloth')
    quantity = int(data.get('item_quantity'))  # Convert quantity to integer
    user_id = session['user_id']

    # Example validation: Check if product_id and quantity are provided
    if not product_id or not quantity:
        return jsonify({'message': 'Product ID and quantity are required.'}), 400

    # Fetch product details from the database
    mycursor = mydb.cursor(dictionary=True)
    sql = "SELECT price FROM cloth_bc WHERE idcloth = %s"
    val = (product_id,)
    mycursor.execute(sql, val)
    product_details = mycursor.fetchone()

    if not product_details:
        return jsonify({'message': 'Product not found.'}), 404

    # Extract price from product_details
    product_price = product_details['price']
    # Calculate total price
    total_price = product_price * quantity

    # Insert product into cart table
    mycursor = mydb.cursor()
    sql = "INSERT INTO cart (cloth_idclothl, user_iduser, item_quantity, totalprice) VALUES (%s, %s, %s, %s)"
    val = (product_id, user_id, quantity, total_price)
    mycursor.execute(sql, val)
    mydb.commit()

    return jsonify({'message': 'Product added to cart successfully.'}), 201


@app.route('/remove_from_cart', methods=['POST'])
def remove_from_cart():
    data = request.get_json()
    product_id = data.get('idcloth')

    # Example validation: Check if product_id is provided
    if not product_id:
        return jsonify({'message': 'Product ID is required.'}), 400

    # Remove product from cart table
    mycursor = mydb.cursor()
    sql = "DELETE FROM cart WHERE cloth_idclothl = %s"
    val = (product_id,)
    mycursor.execute(sql, val)
    mydb.commit()

    return jsonify({'message': 'Product removed from cart successfully.'}), 200

@app.route('/update_cart', methods=['POST'])
def update_cart():
    data = request.get_json()
    product_id = data.get('idcloth')
    quantity = data.get('item_quantity')

    # Check if product_id and quantity are provided
    if not product_id or not quantity:
        return jsonify({'message': 'Product ID and quantity are required.'}), 400

    # Update the quantity for the product in the cart
    mycursor = mydb.cursor()
    sql = "UPDATE cart SET item_quantity = %s WHERE cloth_idclothl = %s"
    val = (quantity, product_id)
    mycursor.execute(sql, val)
    mydb.commit()

    return jsonify({'message': 'Cart updated successfully.'}), 200


@app.route('/view_cart', methods=['GET'])
def view_cart():
    # if 'user_id' not in session:
    #     return jsonify({'message': 'User not logged in'}), 401

    # user_id = session['user_id']

    # Fetch cart items from the database for the logged-in user
    mycursor = mydb.cursor(dictionary=True)
    sql = "SELECT c.cloth_idclothl, c.item_quantity, c.totalprice, p.name, p.price  FROM cart c INNER JOIN cloth_bc p ON c.cloth_idclothl = p.idcloth WHERE c.user_iduser = %s"
    val = (20,)
    mycursor.execute(sql, val)
    cart_items = mycursor.fetchall()

    # Check if cart is empty
    if not cart_items:
        return jsonify({'message': 'Cart is empty'}), 404

    return jsonify(cart_items), 200

@app.route('/add_to_favorites', methods=['POST'])
def add_to_favorites():
    print("Session:", session)
    # if 'user_id' not in session:
    #     return jsonify({'message': 'User not logged in'}), 401

    data = request.get_json()
    product_id = data.get('idcloth')
    # user_id = session['user_id']
    # print("User ID:", user_id)
    print("Product ID:", product_id)
    # Example validation: Check if product_id and quantity are provided
    if not product_id:
        return jsonify({'message': 'Product ID is required.'}), 400
    # Insert product into cart table
    mycursor = mydb.cursor()
    sql = "INSERT INTO favorites (cloth_idcloth, user_iduser) VALUES (%s, %s)"
    val = (product_id, 20)
    mycursor.execute(sql, val)
    mydb.commit()

    return jsonify({'message': 'Product added to favourites successfully.'}), 201

@app.route('/place_order', methods=['POST'])
def place_order():
    if 'user_id' not in session:
        return jsonify({'message': 'User not logged in'}), 401

    user_id = session['user_id']
    data = request.get_json()

    payment_id = data.get('payment_id')

    if not payment_id:
        return jsonify({'message': 'Payment ID is required'}), 400

    try:
        # Fetch all cart items for the user
        mycursor = mydb.cursor(dictionary=True)
        sql = """
            SELECT cloth_idclothl, SUM(item_quantity) as total_quantity, SUM(totalprice) as total_price
            FROM cart
            WHERE user_iduser = %s
            GROUP BY cloth_idclothl
        """
        val = (user_id,)
        mycursor.execute(sql, val)
        cart_items = mycursor.fetchall()

        if not cart_items:
            return jsonify({'message': 'Cart is empty'}), 400

        # Insert combined cart entry
        combined_cart_id = None
        for item in cart_items:
            sql = "INSERT INTO cart (cloth_idclothl, user_iduser, item_quantity, totalprice) VALUES (%s, %s, %s, %s)"
            val = (item['cloth_idclothl'], user_id, item['total_quantity'], item['total_price'])
            mycursor.execute(sql, val)
            if combined_cart_id is None:
                combined_cart_id = mycursor.lastrowid

        # Clear the old cart entries
        sql = "DELETE FROM cart WHERE user_iduser = %s AND idcart != %s"
        mycursor.execute(sql, (user_id, combined_cart_id))
        mydb.commit()

        # Calculate total order price
        total_order_price = sum(item['total_price'] for item in cart_items)

        # Create a new order
        order_date = datetime.now()
        sql = """
            INSERT INTO ordersss (status, date, order_price, payment_idpayment, user_iduser) 
            VALUES (%s, %s, %s, %s, %s)
        """
        val = ('Pending', order_date, total_order_price, payment_id, user_id)
        mycursor.execute(sql, val)
        order_id = mycursor.lastrowid
        # Delete the combined cart entry
        sql = "DELETE FROM cart WHERE idcart = %s"
        mycursor.execute(sql, (combined_cart_id,))

        # Commit all database transactions
        mydb.commit()

        return jsonify({'message': 'Order placed successfully', 'order_id': order_id}), 201

    except Exception as e:
        mydb.rollback()
        return jsonify({'message': f"An unexpected error occurred: {e}"}), 500

    finally:
        mycursor.close()
@app.route('/user/profile', methods=['PUT'])
def update_user_profile():
    data = request.json

    user_id = data.get('user_id')
    if not user_id:
        return jsonify({'message': 'User ID is required'}), 400

    try:
        mycursor = mydb.cursor()

        # Update user profile data
        update_query = "UPDATE user SET username = %(username)s, email = %(email)s, address = %(address)s, phonenumber = %(phone)s WHERE iduser = %(user_id)s"
        mycursor.execute(update_query, data)
        mydb.commit()

        return jsonify({'message': 'User profile updated successfully'})

    except mysql.connector.Error as err:
        mydb.rollback()
        return jsonify({'message': f"Database Error: {err}"}), 500

    except Exception as e:
        mydb.rollback()
        return jsonify({'message': f"An unexpected error occurred: {e}"}), 500
@app.route('/search_product_by_criteria', methods=['GET'])
def search_product_by_criteria():
    # Get search criteria from request parameters
    name = request.args.get('name')
    brand = request.args.get('brand')
    category = request.args.get('category')
    price_min = request.args.get('price_min')
    price_max = request.args.get('price_max')

    # Create cursor
    mycursor = mydb.cursor(dictionary=True)

    # Construct SQL query based on provided criteria
    sql = "SELECT idcloth, name, price, brand, category ,image FROM cloth_bc WHERE 1=1"
    criteria = []
    if name:
        sql += " AND name LIKE %s"
        criteria.append("%" + name + "%")
    if brand:
        sql += " AND brand = %s"
        criteria.append(brand)
    if category:
        sql += " AND category = %s"
        criteria.append(category)
    if price_min:
        sql += " AND price >= %s"
        criteria.append(price_min)
    if price_max:
        sql += " AND price <= %s"
        criteria.append(price_max)

    # Execute SQL query
    mycursor.execute(sql, criteria)
    results = mycursor.fetchall()

    for result in results:
      if isinstance(result['image'], bytes):
        result['image'] = base64.b64encode(result['image']).decode('utf-8')


    return jsonify(results), 200
@app.route('/filter_products', methods=['GET'])
def filter_products():
    # Get filter parameters from request
    gender = request.args.get('gender')
    size = request.args.get('size')
    color = request.args.get('color')

    # Create cursor
    mycursor = mydb.cursor(dictionary=True)

    # Construct SQL query based on provided filters
    sql = "SELECT idcloth, name, price, brand, category, size, color, gender FROM cloth_bc WHERE 1=1"
    filters = []
    if gender:
        sql += " AND gender = %s"
        filters.append(gender)
    if size:
        sql += " AND size = %s"
        filters.append(size)
    if color:
        sql += " AND color = %s"
        filters.append(color)

    # Execute SQL query
    mycursor.execute(sql, filters)
    filtered_products = mycursor.fetchall()

    return jsonify(filtered_products), 200

# Chatbot API endpoint
# @app.route('/chatbot', methods=['POST'])
# def chatbot_endpoint():
#     data = request.json
#     user_input = data.get('user_input')  # Use 'user_input' instead of 'input'
#     response = (user_input)  # Pass user_input to your chatbot function
#     return jsonify({'response': response})

@app.route('/chatbot/entry', methods=['POST'])
def chatbot_entery_endpoint():
    data = request.json
    user_input = data.get('user_input')
    user_choice = data.get('user_choice')

    response = entry(user_input,user_choice)  # Pass user_input to your chatbot function
    return jsonify({'response': response})

if __name__ == '__main__':
    app.secret_key = 'your_secret_key'
    app.run(debug=True)
