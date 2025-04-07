from flask import Flask, render_template, request, session, redirect, url_for
from werkzeug.urls import url_quote
import os
from werkzeug.utils import secure_filename

app = Flask(__name__)
app.secret_key = 'your-secret-key'
app.config['UPLOAD_FOLDER'] = 'static/images'

products = [
    {'id': 1, 'name': 'Book 1', 'price': 10, 'image': None},
    {'id': 2, 'name': 'Book 2', 'price': 15, 'image': None},
    {'id': 3, 'name': 'Book 3', 'price': 20, 'image': None},
]

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        session['logged_in'] = True
        session['username'] = username
        return redirect(url_for('show_products'))
    return render_template('login.html')

@app.route('/products')
def show_products():
    if 'logged_in' not in session:
        return redirect(url_for('login'))
    is_admin = session.get('username') == 'admin'
    return render_template('products.html', products=products, is_admin=is_admin)

@app.route('/manage_products', methods=['GET', 'POST'])
def manage_products():
    if 'logged_in' not in session or session.get('username') != 'admin':
        return redirect(url_for('login'))
    if request.method == 'POST':
        if 'add_product' in request.form:
            name = request.form['name']
            price = float(request.form['price'])
            product = {'id': len(products) + 1, 'name': name, 'price': price, 'image': None}
            products.append(product)
        elif 'edit_product' in request.form:
            product_id = int(request.form['product_id'])
            product = next((p for p in products if p['id'] == product_id), None)
            if product:
                product['name'] = request.form['name']
                product['price'] = float(request.form['price'])
                if 'image' in request.files:
                    image = request.files['image']
                    if image.filename != '':
                        filename = secure_filename(image.filename)
                        image.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
                        product['image'] = url_for('static', filename=f"images/{filename}")
        elif 'delete_product' in request.form:
            product_id = int(request.form['product_id'])
            products[:] = [p for p in products if p['id'] != product_id]
    return render_template('manage_products.html', products=products)

@app.route('/cart')
def show_cart():
    cart = session.get('cart', [])
    total = sum(item['price'] for item in cart)
    return render_template('cart.html', cart=cart, total=total)

@app.route('/add_to_cart/<int:product_id>')
def add_to_cart(product_id):
    product = next((p for p in products if p['id'] == product_id), None)
    if product:
        cart = session.get('cart', [])
        cart.append(product)
        session['cart'] = cart
    return redirect(url_for('show_products'))

@app.route('/checkout')
def checkout():
    session['cart'] = []
    return "Thanh toán thành công!"

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)