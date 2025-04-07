from flask import Flask, render_template, request, session, redirect, url_for
from werkzeug.urls import url_quote
import os
from werkzeug.utils import secure_filename

app = Flask(__name__)
app.secret_key = os.urandom(24)
app.config['UPLOAD_FOLDER'] = 'static/images'

# Tạo thư mục upload nếu chưa tồn tại
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

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

@app.route('/add_product', methods=['GET', 'POST'])
def add_product():
    if session.get('username') != 'admin':
        return redirect(url_for('login'))
    
    if request.method == 'POST':
        name = request.form['name']
        price = float(request.form['price'])
        
        new_id = max(product['id'] for product in products) + 1 if products else 1
        
        new_product = {
            'id': new_id,
            'name': name,
            'price': price,
            'image': None
        }
        
        products.append(new_product)
        return redirect(url_for('manage_products'))
    
    return render_template('add_product.html')

@app.route('/edit_product/<int:product_id>', methods=['GET', 'POST'])
def edit_product(product_id):
    if session.get('username') != 'admin':
        return redirect(url_for('login'))
    
    product = next((p for p in products if p['id'] == product_id), None)
    if not product:
        return redirect(url_for('manage_products'))
    
    if request.method == 'POST':
        product['name'] = request.form['name']
        product['price'] = float(request.form['price'])
        
        if 'image' in request.files:
            image = request.files['image']
            if image.filename != '':
                filename = secure_filename(image.filename)
                image.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
                product['image'] = url_for('static', filename=f"images/{filename}")
        
        return redirect(url_for('manage_products'))
    
    return render_template('edit_product.html', product=product)

@app.route('/delete_product/<int:product_id>', methods=['GET'])
def delete_product(product_id):
    if session.get('username') != 'admin':
        return redirect(url_for('login'))
    
    global products
    products = [p for p in products if p['id'] != product_id]
    return redirect(url_for('manage_products'))

@app.route('/manage_products', methods=['GET'])
def manage_products():
    if session.get('username') != 'admin':
        return redirect(url_for('login'))
    
    return render_template('manage_product.html', products=products)

@app.route('/cart')
def show_cart():
    if 'logged_in' not in session:
        return redirect(url_for('login'))
    
    cart = session.get('cart', [])
    total = sum(item['price'] for item in cart)
    return render_template('cart.html', cart=cart, total=round(total, 2))

@app.route('/add_to_cart/<int:product_id>')
def add_to_cart(product_id):
    if 'logged_in' not in session:
        return redirect(url_for('login'))
    
    product = next((p for p in products if p['id'] == product_id), None)
    if product:
        cart = session.get('cart', [])
        cart_item = product.copy()
        cart.append(cart_item)
        session['cart'] = cart
    return redirect(url_for('show_products'))

@app.route('/checkout')
def checkout():
    if 'logged_in' not in session:
        return redirect(url_for('login'))
    
    total = sum(item['price'] for item in session.get('cart', []))
    session['cart'] = []
    return f"Thanh toán thành công! Tổng tiền: ${total:.2f}"

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)