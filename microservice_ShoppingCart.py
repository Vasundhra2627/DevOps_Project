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
        # Otherwise, add the product to the cart
        else:
            redis_db.hset(user_id, product_id, quantity)
    else:
        redis_db.hset(user_id, product_id, quantity)
    
    return jsonify({'message': 'Product added to cart.'})

@app.route('/get_cart', methods=['GET'])
def get_cart():
    user_id = request.args.get('user_id')
    
    # Check if the user has an existing cart
    if redis_db.exists(user_id):
        cart = {}
        for product_id, quantity in redis_db.hgetall(user_id).items():
            cart[product_id.decode('utf-8')] = int(quantity)
        return jsonify(cart)
    else:
        return jsonify({'message': 'Cart is empty.'})
