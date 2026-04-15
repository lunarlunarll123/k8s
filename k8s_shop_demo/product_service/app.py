from flask import Flask, jsonify, request
from redis import Redis
import socket
import os

app = Flask(__name__)

# [K8s Update] Hostname matches K8s Service Name 'product-redis'
db = Redis(host="product-redis", port=6379, decode_responses=True)

@app.route("/")
def get_products():
    if db.dbsize() == 0:
        db.hset("sku:001", mapping={"name": "iPhone 15 Pro", "stock": 10})
        db.hset("sku:002", mapping={"name": "MacBook Air",   "stock": 5})

    keys = db.keys("sku:*")
    products = {}
    for key in keys:
        products[key] = db.hgetall(key)

    return jsonify({
        "service": "Product Service (K8s)",
        "pod_name": socket.gethostname(),
        "database": "product-redis",
        "data": products
    })

@app.route("/reduce_stock", methods=["POST"])
def reduce_stock():
    data = request.get_json()
    sku = data.get("sku")
    if not db.exists(sku):
        return jsonify({"success": False}), 404
    
    current = int(db.hget(sku, "stock"))
    if current > 0:
        db.hincrby(sku, "stock", -1)
        return jsonify({"success": True, "new_stock": current-1, "name": db.hget(sku, "name")})
    return jsonify({"success": False, "message": "Out of Stock"}), 400

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
