from flask import Flask, render_template, request, session, redirect, url_for, send_from_directory
import os
from werkzeug.utils import secure_filename

app = Flask(__name__)
app.secret_key = os.urandom(24)
app.config['UPLOAD_FOLDER'] = 'static/images'

# Tạo thư mục upload nếu chưa tồn tại
os.makedirs(os.path.join(os.path.dirname(__file__), app.config['UPLOAD_FOLDER']), exist_ok=True)

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
    global products
    
    if session.get('username') != 'admin':
        return redirect(url_for('login'))
    
    if request.method == 'POST':
        # Xử lý thêm sản phẩm
        if 'add_product' in request.form:
            name = request.form['name']
            price = float(request.form['price'])
            new_id = max(p['id'] for p in products) + 1
            new_product = {
                'id': new_id,
                'name': name,
                'price': price,
                'image': None
            }
            products.append(new_product)
        
        # Xử lý sửa sản phẩm
        elif 'edit_product' in request.form:
            product_id = int(request.form['product_id'])
            for product in products:
                if product['id'] == product_id:
                    product['name'] = request.form['name']
                    product['price'] = float(request.form['price'])
                    
                    # Xử lý upload ảnh
                    if 'image' in request.files:
                        image = request.files['image']
                        if image.filename != '':
                            filename = secure_filename(image.filename)
                            file_path = os.path.join(os.path.dirname(__file__), app.config['UPLOAD_FOLDER'], filename)
                            image.save(file_path)
                            product['image'] = f"/static/images/{filename}"
                    break
        
        # Xử lý xóa sản phẩm
        elif 'delete_product' in request.form:
            product_id = int(request.form['product_id'])
            products = [p for p in products if p['id'] != product_id]
    
    return render_template('manage_product.html', products=products)

@app.route('/search', methods=['GET'])
def search_products():
    if 'logged_in' not in session:
        return redirect(url_for('login'))
    
    # Lấy từ khóa tìm kiếm từ query parameter
    query = request.args.get('query', '').lower().strip()
    
    # Tìm kiếm sản phẩm theo tên
    if query:
        search_results = [
            product for product in products 
            if query in product['name'].lower()
        ]
    else:
        search_results = products
    
    is_admin = session.get('username') == 'admin'
    return render_template('products.html', 
                           products=search_results, 
                           is_admin=is_admin, 
                           query=query)

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

@app.route('/cart')
def show_cart():
    if 'logged_in' not in session:
        return redirect(url_for('login'))
    
    cart = session.get('cart', [])
    total = sum(item['price'] for item in cart)
    return render_template('cart.html', cart=cart, total=round(total, 2))

@app.route('/checkout')
def checkout():
    if 'logged_in' not in session:
        return redirect(url_for('login'))
    
    total = sum(item['price'] for item in session.get('cart', []))
    session['cart'] = []
    return f"Thanh toán thành công! Tổng tiền: ${total:.2f}"

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)