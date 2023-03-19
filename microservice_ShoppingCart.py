#this file contains the code for shopping cart microservice, one of the microservices that we are going to use in the project
#coode is written in python language using the flask framework
from flask import Flask, jsonify, request
import redis

app = Flask(__name__)
redis_db = redis.Redis(host='localhost', port=6379, db=0)

@app.route('/add_to_cart', methods=['POST'])
def add_to_cart():
    data = request.json
    user_id = data['user_id']
    product_id = data['product_id']
    quantity = data['quantity']
    
    # Check if the user has an existing cart
    if redis_db.exists(user_id):
        # If the product is already in the cart, update its quantity
        if redis_db.hexists(user_id, product_id):
            current_quantity = int(redis_db.hget(user_id, product_id))
            new_quantity = current_quantity + quantity
            redis_db.hset(user_id, product_id, new_quantity)
        else:
            redis_db.hset(user_id, product_id, quantity)
    else:
        redis_db.hset(user_id, product_id, quantity)
    
    return jsonify({'message': 'Product added to cart.'})

@app.route('/get_cart', methods=['GET'])
def get_cart():
    user_id = request.args.get('user_id')
    
  
    if redis_db.exists(user_id):
        cart = {}
        for product_id, quantity in redis_db.hgetall(user_id).items():
            cart[product_id.decode('utf-8')] = int(quantity)
        return jsonify(cart)
    else:
        return jsonify({'message': 'Cart is empty.'})
    
    @app.route('/remove_from_cart', methods=['DELETE'])
def remove_from_cart():
    data = request.json
    user_id = data['user_id']
    product_id = data['product_id']
    
    if redis_db.exists(user_id):
        if redis_db.hexists(user_id, product_id):
            redis_db.hdel(user_id, product_id)
            return jsonify({'message': 'Product removed from cart.'})
        else:
            return jsonify({'message': 'Product not found in cart.'})
    else:
        return jsonify({'message': 'Cart is empty.'})
    
    
if __name__ == '__main__':
    app.run(debug=True)
    
    
    
import pymysql
from app import app
from db_config import mysql
from flask import flash, session, render_template, request, redirect, url_for
#from werkzeug import generate_password_hash, check_password_hash
from werkzeug.security import generate_password_hash, check_password_hash
		
@app.route('/add', methods=['POST'])
def add_product_to_cart():
	cursor = None
	try:
		_quantity = int(request.form['quantity'])
		_code = request.form['code']
		# validate the received values
		if _quantity and _code and request.method == 'POST':
			conn = mysql.connect()
			cursor = conn.cursor(pymysql.cursors.DictCursor)
			cursor.execute("SELECT * FROM product WHERE code=%s", _code)
			row = cursor.fetchone()
			
			itemArray = { row['code'] : {'name' : row['name'], 'code' : row['code'], 'quantity' : _quantity, 'price' : row['price'], 'image' : row['image'], 'total_price': _quantity * row['price']}}
			
			all_total_price = 0
			all_total_quantity = 0
			
			session.modified = True
			if 'cart_item' in session:
				if row['code'] in session['cart_item']:
					for key, value in session['cart_item'].items():
						if row['code'] == key:
								#session.modified = True
							#if session['cart_item'][key]['quantity'] is not None:
							#	session['cart_item'][key]['quantity'] = 0
							old_quantity = session['cart_item'][key]['quantity']
							total_quantity = old_quantity + _quantity
							session['cart_item'][key]['quantity'] = total_quantity
							session['cart_item'][key]['total_price'] = total_quantity * row['price']
				else:
					session['cart_item'] = array_merge(session['cart_item'], itemArray)

				for key, value in session['cart_item'].items():
					individual_quantity = int(session['cart_item'][key]['quantity'])
					individual_price = float(session['cart_item'][key]['total_price'])
					all_total_quantity = all_total_quantity + individual_quantity
					all_total_price = all_total_price + individual_price
			else:
				session['cart_item'] = itemArray
				all_total_quantity = all_total_quantity + _quantity
				all_total_price = all_total_price + _quantity * row['price']
			session['all_total_quantity'] = all_total_quantity
			session['all_total_price'] = all_total_price
							

