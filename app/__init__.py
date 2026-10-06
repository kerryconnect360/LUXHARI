import os
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from dotenv import load_dotenv

load_dotenv()

db = SQLAlchemy()


def create_app():
    app = Flask(__name__, instance_relative_config=True, static_folder='static')
    os.makedirs(app.instance_path, exist_ok=True)
    os.makedirs(os.path.join(app.root_path, '..', 'uploads'), exist_ok=True)

    app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'dev-change-me')
    database_url = os.getenv('DATABASE_URL')
    if database_url and database_url.startswith('postgres://'):
        database_url = database_url.replace('postgres://', 'postgresql://', 1)
    app.config['SQLALCHEMY_DATABASE_URI'] = database_url or 'sqlite:///' + os.path.join(app.instance_path, 'luxhari.db')
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['UPLOAD_FOLDER'] = os.path.abspath(os.path.join(app.root_path, '..', 'uploads'))
    app.config['MAX_CONTENT_LENGTH'] = 8 * 1024 * 1024

    db.init_app(app)

    from .routes import public_bp, admin_bp
    app.register_blueprint(public_bp)
    app.register_blueprint(admin_bp, url_prefix='/admin')

    with app.app_context():
        from .models import Setting
        db.create_all()
        defaults = {
            'site_name': 'LUXHARI',
            'tagline': 'Wear what inspires you.',
            'business_phone': '',
            'whatsapp': '',
            'contact_email': '',
            'delivery_text': 'Delivery options and timing are confirmed after checkout.',
            'payment_instructions': 'Make your payment using the details shown below, then enter your payment reference.',
            'payment_image': '',
            'logo': '',
            'categories_enabled': 'Clothing,Brands / Collections,Materials,On Model,Home & Living,Accessories,Inspiration',
        }
        for key, value in defaults.items():
            if not Setting.query.filter_by(key=key).first():
                db.session.add(Setting(key=key, value=value))
        from .models import Product
        if Product.query.count() == 0:
            db.session.add_all([
                Product(name='LUXHARI Editorial Dress', category='Clothing', product_type='Clothing', description='A demonstration catalogue piece. Replace with the real LUXHARI collection image and details from Authority.', price=8500, stock=3, sizes='S / M / L / XL', featured=True),
                Product(name='Signature Jacquard', category='Materials', product_type='Material', description='A demonstration material listing. Enter the actual material, colour, texture and stock.', price=1800, unit_label='metre', stock=24),
                Product(name='Velvet Living Set', category='Home & Living', product_type='Home textile', description='A demonstration finished textile product.', price=12500, stock=2),
            ])
            db.session.commit()

    @app.context_processor
    def inject_site():
        from .models import Setting
        settings = {s.key: s.value for s in Setting.query.all()}
        enabled = [x.strip() for x in settings.get('categories_enabled', '').split(',') if x.strip()]
        return {'site': settings, 'enabled_categories': enabled}

    return app
