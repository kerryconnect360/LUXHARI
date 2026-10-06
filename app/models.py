from datetime import datetime, timezone
from . import db


def utcnow():
    return datetime.now(timezone.utc)


class Setting(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    key = db.Column(db.String(100), unique=True, nullable=False)
    value = db.Column(db.Text, nullable=False, default='')


class Product(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(180), nullable=False)
    category = db.Column(db.String(80), nullable=False, default='Clothing')
    product_type = db.Column(db.String(80), nullable=False, default='Product')
    description = db.Column(db.Text, default='')
    price = db.Column(db.Float, nullable=False, default=0)
    unit_label = db.Column(db.String(40), default='item')
    stock = db.Column(db.Float, nullable=False, default=0)
    sizes = db.Column(db.String(200), default='')
    image = db.Column(db.String(500), default='')
    external_image = db.Column(db.String(500), default='')
    featured = db.Column(db.Boolean, default=False)
    custom_order = db.Column(db.Boolean, default=False)
    archived = db.Column(db.Boolean, default=False)
    loves = db.Column(db.Integer, default=0)
    created_at = db.Column(db.DateTime(timezone=True), default=utcnow)


class Order(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    reference = db.Column(db.String(40), unique=True, nullable=False)
    customer_name = db.Column(db.String(180), nullable=False)
    phone = db.Column(db.String(60), nullable=False)
    email = db.Column(db.String(180), default='')
    address = db.Column(db.Text, default='')
    total = db.Column(db.Float, nullable=False, default=0)
    payment_reference = db.Column(db.String(180), default='')
    payment_status = db.Column(db.String(40), default='Pending')
    order_status = db.Column(db.String(40), default='Pending')
    created_at = db.Column(db.DateTime(timezone=True), default=utcnow)
    items = db.relationship('OrderItem', backref='order', cascade='all, delete-orphan')


class OrderItem(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    order_id = db.Column(db.Integer, db.ForeignKey('order.id'), nullable=False)
    product_id = db.Column(db.Integer, db.ForeignKey('product.id'), nullable=True)
    product_name = db.Column(db.String(180), nullable=False)
    price = db.Column(db.Float, nullable=False)
    quantity = db.Column(db.Float, nullable=False, default=1)
    product = db.relationship('Product')
