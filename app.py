# THIS IS AN API FOR Ecommerce Backend
from flask import *
import os
import pymysql
import pymysql.cursors
import cloudinary
import cloudinary.uploader
import cloudinary.api
import requests
import datetime
import base64
from requests.auth import HTTPBasicAuth

# Create the Flask application instance
app = Flask(__name__)

# ---------------------------
# CLOUDINARY CONFIGURATION
# ---------------------------
cloudinary.config(
    cloud_name=os.environ.get('CLOUDINARY_CLOUD_NAME'),
    api_key=os.environ.get('CLOUDINARY_API_KEY'),
    api_secret=os.environ.get('CLOUDINARY_API_SECRET'),
    secure=True
)

# ---------------------------
# SIGNUP ROUTE
# ---------------------------
@app.route('/api/signup', methods=['POST'])
def signup():
    username = request.form['username']
    email = request.form['email']
    password = request.form['password']
    phone = request.form['phone']

    connection = pymysql.connect(host='berxhqu0w65dbve1x0kv-mysql.services.clever-cloud.com',
        user='u8njzekifoc9amwq',
        password='1WNiDxrCA64SljLTWGaU',
        database='berxhqu0w65dbve1x0kv')
    cursor = connection.cursor()
    cursor.execute(
        'INSERT INTO users(username,email,password,phone) VALUES (%s,%s,%s,%s)',
        (username, email, password, phone)
    )
    connection.commit()
    cursor.close()
    connection.close()
    return jsonify({"success": "Thank you for Joining"})

# ---------------------------
# SIGNIN ROUTE
# ---------------------------
@app.route('/api/signin', methods=['POST'])
def signin():
    email = request.form['email']
    password = request.form['password']

    connection = pymysql.connect(host='berxhqu0w65dbve1x0kv-mysql.services.clever-cloud.com',
        user='u8njzekifoc9amwq',
        password='1WNiDxrCA64SljLTWGaU',
        database='berxhqu0w65dbve1x0kv')
    cursor = connection.cursor(pymysql.cursors.DictCursor)
    cursor.execute("SELECT * FROM users WHERE email=%s AND password=%s", (email, password))
    user = cursor.fetchone()
    cursor.close()
    connection.close()

    if user:
        return jsonify({"message": "Login Success", "user": user})
    else:
        return jsonify({"message": "Login Failed"})

# ---------------------------
# ADD PRODUCT ROUTE (Cloudinary)
# ---------------------------
@app.route('/api/add_product', methods=['POST'])
def add_product():
    try:
        product_name = request.form['product_name']
        product_description = request.form['product_description']
        product_cost = request.form['product_cost']
        photo = request.files['product_photo']

        if not photo:
            return jsonify({"error": "No image uploaded"}), 400

        # Upload image to Cloudinary
        upload_result = cloudinary.uploader.upload(photo, folder="products/")
        photo_url = upload_result.get("secure_url")

        # Connect to DB
        connection = pymysql.connect(host='berxhqu0w65dbve1x0kv-mysql.services.clever-cloud.com',
        user='u8njzekifoc9amwq',
        password='1WNiDxrCA64SljLTWGaU',
        database='berxhqu0w65dbve1x0kv')
        cursor = connection.cursor()
        cursor.execute(
            'INSERT INTO product_details (product_name, product_description, product_cost, product_photo) VALUES (%s,%s,%s,%s)',
            (product_name, product_description, product_cost, photo_url)
        )
        connection.commit()
        cursor.close()
        connection.close()

        return jsonify({"success": "Product details added successfully", "photo_url": photo_url})

    except Exception as e:
        return jsonify({"error": str(e)}), 500

# ---------------------------
# GET PRODUCT DETAILS ROUTE
# ---------------------------
@app.route('/api/get_product_details', methods=['GET'])
def get_product_details():
    connection = pymysql.connect(
        host='berxhqu0w65dbve1x0kv-mysql.services.clever-cloud.com',
        user='u8njzekifoc9amwq',
        password='1WNiDxrCA64SljLTWGaU',
        database='berxhqu0w65dbve1x0kv'
    )
    cursor = connection.cursor(pymysql.cursors.DictCursor)
    cursor.execute('SELECT * FROM product_details')
    product_details = cursor.fetchall()
    cursor.close()
    connection.close()
    return jsonify(product_details)

# ---------------------------
# MPESA PAYMENT ROUTE
# ---------------------------
@app.route('/api/mpesa_payment', methods=['POST'])
def mpesa_payment():
    amount = request.form['amount']
    phone = request.form['phone']

    consumer_key = "GTWADFxIpUfDoNikNGqq1C3023evM6UH"
    consumer_secret = "amFbAoUByPV2rM5A"
    api_URL = "https://sandbox.safaricom.co.ke/oauth/v1/generate?grant_type=client_credentials"
    r = requests.get(api_URL, auth=HTTPBasicAuth(consumer_key, consumer_secret))
    access_token = "Bearer " + r.json()['access_token']

    timestamp = datetime.datetime.today().strftime('%Y%m%d%H%M%S')
    passkey = 'bfb279f9aa9bdbcf158e97dd71a467cd2e0c893059b10f78e6b72ada1ed2c919'
    business_short_code = "174379"
    data = business_short_code + passkey + timestamp
    password = base64.b64encode(data.encode()).decode('utf-8')

    payload = {
        "BusinessShortCode": "174379",
        "Password": password,
        "Timestamp": timestamp,
        "TransactionType": "CustomerPayBillOnline",
        "Amount": "1",
        "PartyA": phone,
        "PartyB": "174379",
        "PhoneNumber": phone,
        "CallBackURL": "https://modcom.co.ke/api/confirmation.php",
        "AccountReference": "account",
        "TransactionDesc": "account"
    }

    headers = {"Authorization": access_token, "Content-Type": "application/json"}
    url = "https://sandbox.safaricom.co.ke/mpesa/stkpush/v1/processrequest"
    response = requests.post(url, json=payload, headers=headers)
    print(response.text)
    return jsonify({"message": "Please Complete Payment in Your Phone and we will deliver in minutes"})

# ---------------------------
# RUN THE APP
# ---------------------------
if __name__ == '__main__':
    app.run(debug=True)
