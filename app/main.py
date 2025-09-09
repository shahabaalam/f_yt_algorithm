from flask import Flask, request, jsonify, render_template
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def create_app():
    app = Flask(__name__)
    
    # Configuration
    app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'dev-key-for-testing')
    app.config['YOUTUBE_API_KEY'] = os.getenv('YOUTUBE_API_KEY', '')
    
    # Initialize database
    from app.database import init_db
    init_db()
    
    # Import and register blueprints
    from app.routes import api_bp
    app.register_blueprint(api_bp)
    
    @app.route('/')
    def index():
        return render_template('index.html')
    
    return app

if __name__ == '__main__':
    app = create_app()
    app.run(debug=True, host='0.0.0.0', port=5000)
