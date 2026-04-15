from flask import Flask, request, render_template_string
from redis import Redis
import socket
import requests

app = Flask(__name__)

# [K8s Update] Hostname matches K8s Service Name 'order-redis'
db = Redis(host="order-redis", port=6379, decode_responses=True)

HTML = """
<!DOCTYPE html>
<html>
<body style="padding:40px; font-family:sans-serif;">
    <h1>Kubernetes Shop 🛒</h1>
    <p>Pod: <b>{{ pod }}</b></p>
    
    <form action="/order/submit" method="POST">
        <select name="sku">
            <option value="sku:001">iPhone 15</option>
            <option value="sku:002">MacBook</option>
        </select>
        <button type="submit">Order Now</button>
    </form>
    
    <h3>History</h3>
    <ul>{% for log in logs %}<li>{{ log }}</li>{% endfor %}</ul>
</body>
</html>
"""

@app.route("/")
def index():
    logs = db.lrange("history", 0, 5)
    return render_template_string(HTML, logs=logs, pod=socket.gethostname())

@app.route("/submit", methods=["POST"])
def submit():
    sku = request.form["sku"]
    try:
        # [K8s Update] Call 'product-service' (K8s Service Name)
        res = requests.post("http://product-service:5000/reduce_stock", json={"sku": sku})
        data = res.json()
        if res.status_code == 200 and data["success"]:
            oid = db.incr("id")
            msg = f"Order #{oid}: {data['name']} (Stock: {data['new_stock']})"
            db.lpush("history", msg)
            return f"<h2>Success</h2><p>{msg}</p><a href='/order/'>Back</a>"
        return f"<h2>Failed</h2><p>{data.get('message')}</p><a href='/order/'>Back</a>"
    except Exception as e:
        return f"Error connecting to Product Service: {e}"

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
