import os
import hashlib
from datetime import timedelta
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from dotenv import load_dotenv

load_dotenv()

db = SQLAlchemy()


def create_app():
    app = Flask(__name__, instance_relative_config=True, static_folder='static')
    os.makedirs(app.instance_path, exist_ok=True)
    os.makedirs(os.path.join(app.root_path, '..', 'uploads'), exist_ok=True)

    # No extra SECRET_KEY environment variable is required. A stable key is derived
    # from the existing admin environment values so login sessions survive Render restarts.
    username = os.getenv('USER_NAME', 'admin')
    password = os.getenv('USER_PASSWORD', 'change-this-password')
    app.config['SECRET_KEY'] = hashlib.sha256(f'{username}::{password}::LUXHARI'.encode()).hexdigest()
    app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(days=7)
    app.config['SESSION_COOKIE_HTTPONLY'] = True
    app.config['SESSION_COOKIE_SAMESITE'] = 'Lax'
    # Render serves the live site over HTTPS; secure cookies keep the admin session reliable.
    # For local HTTP development, set LUXHARI_LOCAL_HTTP=1 to disable the secure flag.
    app.config['SESSION_COOKIE_SECURE'] = os.getenv('LUXHARI_LOCAL_HTTP', '').strip() != '1'
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
        from .seed_catalog import ensure_starter_catalog
        ensure_starter_catalog()
        db.session.commit()

    @app.context_processor
    def inject_site():
        from .models import Setting
        settings = {s.key: s.value for s in Setting.query.all()}
        enabled = [x.strip() for x in settings.get('categories_enabled', '').split(',') if x.strip()]
        return {'site': settings, 'enabled_categories': enabled}

    return app
