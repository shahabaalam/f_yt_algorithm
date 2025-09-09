from flask import Blueprint, request, jsonify
from app.youtube_api import search_videos, get_video_details
from app.recommendations import get_recommendations
from app.database import add_watch_history, get_watch_history

api_bp = Blueprint('api', __name__)

@api_bp.route('/api/search', methods=['GET'])
def search():
    query = request.args.get('q', '')
    max_results = int(request.args.get('max_results', 10))
    
    if not query:
        return jsonify({'error': 'Query parameter is required'}), 400
    
    try:
        videos = search_videos(query, max_results)
        return jsonify({'videos': videos})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@api_bp.route('/api/recommendations', methods=['GET'])
def recommendations():
    user_id = request.args.get('user_id', 'default')
    limit = int(request.args.get('limit', 10))
    
    try:
        recs = get_recommendations(user_id, limit)
        return jsonify({'recommendations': recs})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@api_bp.route('/api/watch_history', methods=['POST'])
def add_to_history():
    data = request.get_json()
    user_id = data.get('user_id', 'default')
    video_id = data.get('video_id')
    
    if not video_id:
        return jsonify({'error': 'video_id is required'}), 400
    
    try:
        add_watch_history(user_id, video_id)
        return jsonify({'success': True})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@api_bp.route('/api/watch_history', methods=['GET'])
def get_history():
    user_id = request.args.get('user_id', 'default')
    limit = int(request.args.get('limit', 20))
    
    try:
        history = get_watch_history(user_id, limit)
        return jsonify({'history': history})
    except Exception as e:
        return jsonify({'error': str(e)}), 500
