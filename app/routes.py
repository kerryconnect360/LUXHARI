import os
import uuid
import hmac
from functools import wraps
from decimal import Decimal
from flask import Blueprint, current_app, render_template, request, redirect, url_for, session, flash, send_from_directory, abort, jsonify
from werkzeug.utils import secure_filename
from . import db
from .models import Product, Order, OrderItem, Setting

public_bp = Blueprint('public', __name__)
admin_bp = Blueprint('admin', __name__)

CATEGORIES = ['Clothing', 'Brands / Collections', 'Materials', 'On Model', 'Home & Living', 'Accessories', 'Inspiration']
STATUSES = ['Pending', 'Payment initiated', 'Paid', 'Processing', 'Ready / Shipped', 'Completed', 'Cancelled']
ALLOWED_EXT = {'jpg', 'jpeg', 'png', 'webp'}


def get_setting(key, default=''):
    row = Setting.query.filter_by(key=key).first()
    return row.value if row else default


def admin_required(fn):
    @wraps(fn)
    def wrapped(*args, **kwargs):
        if not session.get('admin_logged_in'):
            return redirect(url_for('admin.login', next=request.path))
        return fn(*args, **kwargs)
    return wrapped


def save_upload(file_storage, prefix='image'):
    if not file_storage or not file_storage.filename:
        return ''
    ext = file_storage.filename.rsplit('.', 1)[-1].lower() if '.' in file_storage.filename else ''
    if ext not in ALLOWED_EXT:
        return ''
    filename = f"{prefix}-{uuid.uuid4().hex[:12]}.{ext}"
    path = os.path.join(current_app.config['UPLOAD_FOLDER'], secure_filename(filename))
    file_storage.save(path)
    return filename


def money(value):
    return f"KSh {value:,.2f}"


@public_bp.route('/')
def home():
    selected = request.args.get('category', '').strip()
    query = Product.query.filter_by(archived=False)
    enabled = [x.strip() for x in get_setting('categories_enabled', '').split(',') if x.strip()]
    if selected and selected in CATEGORIES and selected in enabled:
        query = query.filter_by(category=selected)
    page = max(1, request.args.get('page', 1, type=int) or 1)
    pagination = query.order_by(Product.featured.desc(), Product.created_at.desc()).paginate(page=page, per_page=48, error_out=False)
    return render_template('home.html', products=pagination.items, pagination=pagination, categories=CATEGORIES, selected=selected)


@public_bp.route('/product/<int:product_id>')
def product(product_id):
    item = Product.query.get_or_404(product_id)
    if item.archived:
        abort(404)
    related = Product.query.filter(Product.category == item.category, Product.id != item.id, Product.archived.is_(False)).order_by(Product.created_at.desc()).limit(4).all()
    return render_template('product.html', product=item, related=related)


@public_bp.route('/media/<path:filename>')
def media(filename):
    response = send_from_directory(current_app.config['UPLOAD_FOLDER'], filename)
    response.headers['Cache-Control'] = 'public, max-age=31536000, immutable'
    return response


@public_bp.route('/manifest.json')
def manifest():
    return jsonify({
        'name': get_setting('site_name', 'LUXHARI'),
        'short_name': 'LUXHARI',
        'start_url': '/',
        'display': 'standalone',
        'background_color': '#07111c',
        'theme_color': '#07111c',
        'icons': [{'src': url_for('public.pwa_icon'), 'sizes': '192x192', 'type': 'image/png'}]
    })


@public_bp.route('/pwa-icon.png')
def pwa_icon():
    logo = get_setting('logo')
    if logo and os.path.exists(os.path.join(current_app.config['UPLOAD_FOLDER'], logo)):
        return send_from_directory(current_app.config['UPLOAD_FOLDER'], logo)
    from PIL import Image, ImageDraw, ImageFont
    from io import BytesIO
    image = Image.new('RGB', (192, 192), '#07111c')
    draw = ImageDraw.Draw(image)
    draw.rectangle((16, 16, 176, 176), outline='#c9a45a', width=4)
    draw.text((96, 96), 'L', fill='#f2eadc', anchor='mm')
    buf = BytesIO(); image.save(buf, format='PNG'); buf.seek(0)
    return buf.read(), 200, {'Content-Type': 'image/png'}


@public_bp.route('/service-worker.js')
def service_worker():
    response = current_app.make_response(render_template('service-worker.js'))
    response.headers['Content-Type'] = 'application/javascript'
    response.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate, max-age=0'
    response.headers['Pragma'] = 'no-cache'
    return response


@public_bp.route('/cart')
def cart():
    cart_items = []
    total = Decimal('0')
    raw = session.get('cart', {})
    for product_id, qty in raw.items():
        item = Product.query.get(int(product_id))
        if item and not item.archived:
            qtyd = Decimal(str(qty))
            subtotal = Decimal(str(item.price)) * qtyd
            total += subtotal
            cart_items.append({'product': item, 'quantity': qty, 'subtotal': subtotal})
    return render_template('cart.html', cart_items=cart_items, total=total)


@public_bp.post('/cart/add/<int:product_id>')
def add_cart(product_id):
    item = Product.query.get_or_404(product_id)
    if item.custom_order:
        return redirect(url_for('public.product', product_id=item.id))
    if item.stock <= 0:
        flash('This item is currently unavailable.', 'error')
        return redirect(request.referrer or url_for('public.home'))
    cart = session.setdefault('cart', {})
    key = str(item.id)
    current = float(cart.get(key, 0))
    cart[key] = min(item.stock, current + 1)
    session.modified = True
    flash(f'{item.name} added to your bag.', 'success')
    return redirect(request.referrer or url_for('public.home'))


@public_bp.post('/cart/update')
def update_cart():
    cart = session.setdefault('cart', {})
    for key, value in request.form.items():
        if key.startswith('qty_'):
            pid = key.split('_', 1)[1]
            try:
                qty = max(0, float(value))
                item = Product.query.get(int(pid))
                cart[pid] = min(qty, item.stock if item else qty)
                if cart[pid] == 0:
                    cart.pop(pid, None)
            except ValueError:
                pass
    session.modified = True
    return redirect(url_for('public.cart'))


@public_bp.get('/checkout')
def checkout():
    if not session.get('cart'):
        return redirect(url_for('public.cart'))
    return render_template('checkout.html', payment_instructions=get_setting('payment_instructions'), payment_image=get_setting('payment_image'))


@public_bp.post('/checkout')
def create_order():
    raw = session.get('cart', {})
    if not raw:
        return redirect(url_for('public.cart'))
    customer_name = request.form.get('customer_name', '').strip()
    phone = request.form.get('phone', '').strip()
    email = request.form.get('email', '').strip()
    address = request.form.get('address', '').strip()
    payment_reference = request.form.get('payment_reference', '').strip()
    if not customer_name or not phone:
        flash('Please provide your name and phone number.', 'error')
        return redirect(url_for('public.checkout'))

    order = Order(reference='LH-' + uuid.uuid4().hex[:10].upper(), customer_name=customer_name, phone=phone, email=email, address=address)
    total = 0.0
    for pid, qty in raw.items():
        item = Product.query.get(int(pid))
        if not item or item.archived or item.stock < float(qty):
            flash(f'{item.name if item else "An item"} is no longer available in that quantity.', 'error')
            return redirect(url_for('public.cart'))
        total += item.price * float(qty)
        order.items.append(OrderItem(product_id=item.id, product_name=item.name, price=item.price, quantity=float(qty)))
        item.stock -= float(qty)
    order.total = total
    order.payment_reference = payment_reference
    order.payment_status = 'Payment initiated' if payment_reference else 'Pending'
    order.order_status = 'Payment initiated' if payment_reference else 'Pending'
    db.session.add(order)
    db.session.commit()
    session['cart'] = {}
    session['last_order_ref'] = order.reference
    return redirect(url_for('public.receipt', reference=order.reference))


@public_bp.route('/receipt/<reference>')
def receipt(reference):
    order = Order.query.filter_by(reference=reference).first_or_404()
    return render_template('receipt.html', order=order)


@public_bp.route('/track', methods=['GET', 'POST'])
def track():
    order = None
    searched = False
    if request.method == 'POST':
        searched = True
        ref = request.form.get('reference', '').strip().upper()
        phone = request.form.get('phone', '').strip()
        order = Order.query.filter_by(reference=ref, phone=phone).first()
    return render_template('track.html', order=order, searched=searched)


@public_bp.get('/interests')
def interests():
    return render_template('interests.html')


@public_bp.get('/about')
def about():
    return render_template('about.html')


@admin_bp.after_request
def admin_no_cache(response):
    response.headers['Cache-Control'] = 'no-store, no-cache, must-revalidate, max-age=0'
    response.headers['Pragma'] = 'no-cache'
    return response


@admin_bp.route('/login', methods=['GET', 'POST'])
def login():
    configured_username = os.environ.get('USER_NAME', 'admin')
    configured_password = os.environ.get('USER_PASSWORD', 'change-this-password')

    def clean_env_value(value):
        value = (value or '').strip()
        if len(value) >= 2 and value[0] == value[-1] and value[0] in {'\"', "'"}:
            value = value[1:-1].strip()
        return value

    configured_username = clean_env_value(configured_username)
    configured_password = clean_env_value(configured_password)
    if request.method == 'POST':
        username = clean_env_value(request.form.get('username', ''))
        password = clean_env_value(request.form.get('password', ''))
        username_ok = hmac.compare_digest(username, configured_username)
        password_ok = hmac.compare_digest(password, configured_password)
        # USER_NAME/USER_PASSWORD are authoritative. The aliases are only a compatibility
        # safety net for old Render services that may still carry USERNAME/PASSWORD.
        if not (username_ok and password_ok):
            legacy_username = os.environ.get('USERNAME')
            legacy_password = os.environ.get('PASSWORD')
            if legacy_username and legacy_password:
                username_ok = hmac.compare_digest(username, clean_env_value(legacy_username))
                password_ok = hmac.compare_digest(password, clean_env_value(legacy_password))
        if username_ok and password_ok:
            session.clear()
            session.permanent = True
            session['admin_logged_in'] = True
            session['admin_user'] = configured_username
            return redirect(request.args.get('next') or url_for('admin.dashboard'))
        flash('The admin login did not match USER_NAME / USER_PASSWORD. Check the Render values exactly, then try again.', 'error')
    return render_template('admin/login.html')


@public_bp.route('/pulse_receiver', methods=['POST', 'GET'])
def pulse_receiver():
    # Compatibility endpoint for harmless external uptime/pulse checks.
    return ('', 204)


@admin_bp.get('/logout')
def logout():
    session.pop('admin_logged_in', None)
    return redirect(url_for('public.home'))


@admin_bp.get('/')
@admin_required
def dashboard():
    from sqlalchemy import func
    stats = {
        'orders': Order.query.count(),
        'sales': db.session.query(func.coalesce(func.sum(Order.total), 0)).filter(Order.payment_status == 'Paid').scalar() or 0,
        'products': Product.query.filter_by(archived=False).count(),
        'loved': db.session.query(func.coalesce(func.sum(Product.loves), 0)).scalar() or 0,
    }
    recent = Order.query.order_by(Order.created_at.desc()).limit(8).all()
    low_stock = Product.query.filter(Product.archived.is_(False), Product.stock <= 3).order_by(Product.stock.asc()).limit(8).all()
    return render_template('admin/dashboard.html', stats=stats, recent=recent, low_stock=low_stock)


@admin_bp.get('/products')
@admin_required
def products():
    items = Product.query.order_by(Product.created_at.desc()).all()
    return render_template('admin/products.html', products=items, categories=CATEGORIES)


@admin_bp.route('/products/new', methods=['GET', 'POST'])
@admin_required
def new_product():
    if request.method == 'POST':
        image = save_upload(request.files.get('image'), 'product') or request.form.get('external_image', '').strip()
        item = Product(name=request.form.get('name', '').strip(), category=request.form.get('category', 'Clothing'), product_type=request.form.get('product_type', 'Product'), description=request.form.get('description', '').strip(), price=float(request.form.get('price') or 0), unit_label=request.form.get('unit_label', 'item'), stock=float(request.form.get('stock') or 0), sizes=request.form.get('sizes', '').strip(), image=image, featured=bool(request.form.get('featured')), custom_order=bool(request.form.get('custom_order')))
        if not item.name:
            flash('Product name is required.', 'error')
            return render_template('admin/product_form.html', product=None, categories=CATEGORIES)
        db.session.add(item); db.session.commit()
        flash('Product created.', 'success')
        return redirect(url_for('admin.products'))
    return render_template('admin/product_form.html', product=None, categories=CATEGORIES)


@admin_bp.route('/products/<int:product_id>/edit', methods=['GET', 'POST'])
@admin_required
def edit_product(product_id):
    item = Product.query.get_or_404(product_id)
    if request.method == 'POST':
        new_image = save_upload(request.files.get('image'), 'product')
        item.name = request.form.get('name', item.name).strip()
        item.category = request.form.get('category', item.category)
        item.product_type = request.form.get('product_type', item.product_type)
        item.description = request.form.get('description', '').strip()
        item.price = float(request.form.get('price') or 0)
        item.unit_label = request.form.get('unit_label', 'item').strip()
        item.stock = float(request.form.get('stock') or 0)
        item.sizes = request.form.get('sizes', '').strip()
        item.external_image = request.form.get('external_image', '').strip()
        if new_image: item.image = new_image
        elif item.external_image: item.image = item.external_image
        item.featured = bool(request.form.get('featured'))
        item.custom_order = bool(request.form.get('custom_order'))
        db.session.commit()
        flash('Product updated.', 'success')
        return redirect(url_for('admin.products'))
    return render_template('admin/product_form.html', product=item, categories=CATEGORIES)


@admin_bp.post('/products/<int:product_id>/archive')
@admin_required
def archive_product(product_id):
    item = Product.query.get_or_404(product_id)
    item.archived = not item.archived
    db.session.commit()
    flash('Product visibility updated.', 'success')
    return redirect(url_for('admin.products'))


@admin_bp.post('/products/<int:product_id>/love')
@admin_required
def reset_loves(product_id):
    item = Product.query.get_or_404(product_id)
    item.loves = 0
    db.session.commit()
    return redirect(url_for('admin.products'))


@admin_bp.get('/orders')
@admin_required
def orders():
    return render_template('admin/orders.html', orders=Order.query.order_by(Order.created_at.desc()).all(), statuses=STATUSES)


@admin_bp.post('/orders/<int:order_id>/status')
@admin_required
def update_order(order_id):
    order = Order.query.get_or_404(order_id)
    order.order_status = request.form.get('order_status', order.order_status)
    if request.form.get('payment_status') in ['Pending', 'Payment initiated', 'Paid']:
        order.payment_status = request.form.get('payment_status')
    if order.payment_status == 'Paid' and order.order_status in ['Pending', 'Payment initiated']:
        order.order_status = 'Processing'
    db.session.commit()
    flash('Order updated.', 'success')
    return redirect(url_for('admin.orders'))


@admin_bp.route('/settings', methods=['GET', 'POST'])
@admin_required
def settings():
    settings = {s.key: s.value for s in Setting.query.all()}
    if request.method == 'POST':
        keys = ['site_name', 'tagline', 'business_phone', 'whatsapp', 'contact_email', 'delivery_text', 'payment_instructions']
        for key in keys:
            val = request.form.get(key, '').strip()
            row = Setting.query.filter_by(key=key).first()
            row.value = val
        enabled = request.form.getlist('categories_enabled')
        Setting.query.filter_by(key='categories_enabled').first().value = ','.join(enabled)
        logo = save_upload(request.files.get('logo'), 'logo')
        payment_image = save_upload(request.files.get('payment_image'), 'payment')
        if logo: Setting.query.filter_by(key='logo').first().value = logo
        if payment_image: Setting.query.filter_by(key='payment_image').first().value = payment_image
        db.session.commit()
        flash('LUXHARI settings saved.', 'success')
        return redirect(url_for('admin.settings'))
    return render_template('admin/settings.html', settings=settings, categories=CATEGORIES)


@public_bp.post('/api/love/<int:product_id>')
def love(product_id):
    item = Product.query.get_or_404(product_id)
    item.loves += 1
    db.session.commit()
    return jsonify({'loves': item.loves})
