import os
import logging
from flask import Flask, render_template, redirect, url_for, send_from_directory, request, jsonify
from werkzeug.utils import secure_filename
from config import Config
from models.database import init_db
from extensions import limiter, csrf

# Configure central application logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] [%(name)s] %(message)s'
)
logger = logging.getLogger('agrismart')

def create_app():
    app = Flask(__name__)
    app.url_map.strict_slashes = False
    app.config.from_object(Config)

    # Initialize extensions
    limiter.init_app(app)
    csrf.init_app(app)

    # Initialize SQLite database with tables and seed records safely
    with app.app_context():
        init_db()

    # Register Blueprints
    from routes.auth import auth_bp
    from routes.dashboard import dashboard_bp
    from routes.weather import weather_bp
    from routes.crop import crop_bp
    from routes.soil import soil_bp
    from routes.mandi import mandi_bp
    from routes.disease import disease_bp
    from routes.profile import profile_bp
    from routes.settings import settings_bp
    from routes.admin import admin_bp

    app.register_blueprint(auth_bp)
    app.register_blueprint(dashboard_bp)
    app.register_blueprint(weather_bp)
    app.register_blueprint(crop_bp)
    app.register_blueprint(soil_bp)
    app.register_blueprint(mandi_bp)
    app.register_blueprint(disease_bp)
    app.register_blueprint(profile_bp)
    app.register_blueprint(settings_bp)
    app.register_blueprint(admin_bp)

    # Secure Uploaded File Serving
    @app.route('/static/uploads/<path:filename>')
    def uploaded_file(filename):
        safe_name = secure_filename(os.path.basename(filename))
        upload_dir = os.path.abspath(app.config['UPLOAD_FOLDER'])
        target_path = os.path.abspath(os.path.join(upload_dir, safe_name))
        
        # Verify path containment
        if not target_path.startswith(upload_dir) or not os.path.exists(target_path):
            return render_template('base.html', not_found=True), 404
            
        return send_from_directory(upload_dir, safe_name)

    # HTTP Security Headers Middleware
    @app.after_request
    def set_security_headers(response):
        response.headers['X-Content-Type-Options'] = 'nosniff'
        response.headers['X-Frame-Options'] = 'SAMEORIGIN'
        response.headers['X-XSS-Protection'] = '1; mode=block'
        response.headers['Referrer-Policy'] = 'strict-origin-when-cross-origin'
        
        # Compatible Content Security Policy permitting necessary CDNs (Fonts, Icons, Charts)
        csp_policy = (
            "default-src 'self'; "
            "script-src 'self' 'unsafe-inline' https://cdn.jsdelivr.net https://cdnjs.cloudflare.com; "
            "style-src 'self' 'unsafe-inline' https://fonts.googleapis.com https://cdnjs.cloudflare.com; "
            "font-src 'self' https://fonts.gstatic.com https://cdnjs.cloudflare.com data:; "
            "img-src 'self' data: blob: https:; "
            "connect-src 'self' https:; "
            "frame-ancestors 'self';"
        )
        response.headers['Content-Security-Policy'] = csp_policy
        return response

    # Helper function for JSON error responses
    def wants_json():
        return (
            request.path.startswith('/api/') or
            request.path.startswith('/disease/api/') or
            request.path.startswith('/weather/api/') or
            request.is_json or
            request.headers.get('Accept') == 'application/json' or
            request.headers.get('X-Requested-With') == 'XMLHttpRequest'
        )

    # Global Safe Error Handlers (Never expose stack traces or database internals)
    @app.errorhandler(400)
    def bad_request(e):
        if wants_json():
            return jsonify({'status': 'error', 'error': 'Bad Request', 'message': str(getattr(e, 'description', 'Invalid request parameters.'))}), 400
        return render_template('base.html', error_title="400 - Bad Request", error_msg="The server could not understand your request."), 400

    @app.errorhandler(401)
    def unauthorized(e):
        if wants_json():
            return jsonify({'status': 'error', 'error': 'Unauthorized', 'message': 'Authentication required. Please sign in.'}), 401
        return redirect(url_for('auth.login', next=request.path))

    @app.errorhandler(403)
    def forbidden(e):
        if wants_json():
            return jsonify({'status': 'error', 'error': 'Forbidden', 'message': 'Access denied: You do not have permission to access this resource.'}), 403
        return render_template('base.html', error_title="403 - Access Forbidden", error_msg="You do not have permission to access this protected area."), 403

    @app.errorhandler(404)
    def page_not_found(e):
        if wants_json():
            return jsonify({'status': 'error', 'error': 'Not Found', 'message': 'The requested resource was not found.'}), 404
        return render_template('base.html', not_found=True), 404

    @app.errorhandler(413)
    def request_entity_too_large(e):
        if wants_json():
            return jsonify({'status': 'error', 'error': 'Payload Too Large', 'message': 'Uploaded file exceeds maximum permitted file size (16 MB).'}), 413
        return render_template('base.html', error_title="413 - File Too Large", error_msg="The uploaded file exceeds the 16 MB limit."), 413

    @app.errorhandler(429)
    def ratelimit_handler(e):
        if wants_json():
            return jsonify({'status': 'error', 'error': 'Too Many Requests', 'message': 'Rate limit exceeded. Please wait a moment before trying again.'}), 429
        return render_template('base.html', error_title="429 - Rate Limit Exceeded", error_msg="You have made too many requests in a short time. Please slow down."), 429

    @app.errorhandler(500)
    def server_error(e):
        logger.exception(f"Internal server error on {request.path}: {e}")
        if wants_json():
            return jsonify({'status': 'error', 'error': 'Internal Server Error', 'message': 'An unexpected error occurred. Please contact the administrator.'}), 500
        return render_template('base.html', error_title="500 - Server Error", error_msg="An unexpected error occurred. Our team has been notified."), 500

    return app

app = create_app()

if __name__ == '__main__':
    debug_mode = os.environ.get('FLASK_DEBUG', 'False').lower() in ('true', '1')
    app.run(host='0.0.0.0', port=5000, debug=debug_mode)
