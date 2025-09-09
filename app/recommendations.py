import numpy as np
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.decomposition import TruncatedSVD
from collections import defaultdict
import json
from app.database import get_user_interactions, get_video_metadata, save_video_metadata
from app.youtube_api import get_video_details

class HybridRecommender:
    def __init__(self):
        self.content_vectorizer = TfidfVectorizer(
            max_features=1000,
            stop_words='english',
            ngram_range=(1, 2)
        )
        self.video_features = {}
        self.user_profiles = {}
        
    def extract_video_features(self, video_data):
        """Extract text features from video metadata"""
        features = []
        
        # Title
        if video_data.get('title'):
            features.append(str(video_data['title']))
        
        # Description
        if video_data.get('description'):
            features.append(str(video_data['description']))
        
        # Tags
        if video_data.get('tags'):
            features.append(' '.join(str(tag) for tag in video_data['tags']))
        
        # Channel
        if video_data.get('channel_title'):
            features.append(str(video_data['channel_title']))
        
        return ' '.join(features)
    
    def build_content_features(self, video_ids):
        """Build TF-IDF features for content-based filtering"""
        video_texts = []
        valid_video_ids = []
        
        for video_id in video_ids:
            # Get video metadata
            video_data = get_video_metadata(video_id)
            if not video_data:
                # Fetch from YouTube API if not in database
                try:
                    video_data = get_video_details(video_id)
                    if video_data:
                        save_video_metadata(video_data)
                except:
                    continue
            
            if video_data:
                text_features = self.extract_video_features(video_data)
                if text_features:
                    video_texts.append(text_features)
                    valid_video_ids.append(video_id)
                    self.video_features[video_id] = text_features
        
        if video_texts:
            # Fit TF-IDF vectorizer
            tfidf_matrix = self.content_vectorizer.fit_transform(video_texts)
            return tfidf_matrix, valid_video_ids
        
        return None, []
    
    def content_based_recommendations(self, watched_videos, candidate_videos, top_n=10):
        """Generate content-based recommendations"""
        if not watched_videos or not candidate_videos:
            return []
        
        # Get features for all videos
        all_video_ids = list(set(watched_videos + candidate_videos))
        tfidf_matrix, valid_ids = self.build_content_features(all_video_ids)
        
        if tfidf_matrix is None or len(valid_ids) < 2:
            return []
        
        # Create mapping from video_id to index
        id_to_idx = {vid: idx for idx, vid in enumerate(valid_ids)}
        
        # Get indices of watched videos and candidate videos
        watched_indices = [id_to_idx[vid] for vid in watched_videos if vid in id_to_idx]
        candidate_indices = [id_to_idx[vid] for vid in candidate_videos if vid in id_to_idx]
        
        if not watched_indices or not candidate_indices:
            return []
        
        # Calculate similarity between watched videos and candidates
        watched_features = tfidf_matrix[watched_indices]
        candidate_features = tfidf_matrix[candidate_indices]
        
        similarities = cosine_similarity(watched_features, candidate_features)
        
        # Average similarity across all watched videos
        avg_similarities = np.mean(similarities, axis=0)
        
        # Get top recommendations
        top_indices = np.argsort(avg_similarities)[::-1][:top_n]
        
        recommendations = []
        for idx in top_indices:
            video_id = valid_ids[candidate_indices[idx]]
            score = float(avg_similarities[idx])
            recommendations.append({
                'video_id': video_id,
                'score': score,
                'type': 'content-based'
            })
        
        return recommendations
    
    def collaborative_filtering_recommendations(self, user_id, all_users_interactions, candidate_videos, top_n=10):
        """Simple collaborative filtering based on user interactions"""
        if not all_users_interactions or not candidate_videos:
            return []
        
        # Build user-item matrix
        user_videos = defaultdict(set)
        video_users = defaultdict(set)
        
        for interaction in all_users_interactions:
            uid = interaction['user_id']
            vid = interaction['video_id']
            user_videos[uid].add(vid)
            video_users[vid].add(uid)
        
        if user_id not in user_videos:
            return []
        
        user_watched = user_videos[user_id]
        
        # Calculate similarity between users based on Jaccard similarity
        user_similarities = {}
        target_user_videos = user_videos[user_id]
        
        for other_user, other_videos in user_videos.items():
            if other_user == user_id:
                continue
            
            intersection = len(target_user_videos.intersection(other_videos))
            union = len(target_user_videos.union(other_videos))
            
            if union > 0:
                similarity = intersection / union
                user_similarities[other_user] = similarity
        
        # Get top similar users
        top_similar_users = sorted(user_similarities.items(), key=lambda x: x[1], reverse=True)[:20]
        
        # Score candidate videos based on similar users' preferences
        video_scores = defaultdict(float)
        
        for similar_user, similarity in top_similar_users:
            similar_user_videos = user_videos[similar_user]
            for video_id in similar_user_videos:
                if video_id not in user_watched and video_id in candidate_videos:
                    video_scores[video_id] += similarity
        
        # Sort by score and return top recommendations
        recommendations = []
        for video_id, score in sorted(video_scores.items(), key=lambda x: x[1], reverse=True)[:top_n]:
            recommendations.append({
                'video_id': video_id,
                'score': float(score),
                'type': 'collaborative'
            })
        
        return recommendations
    
    def hybrid_recommendations(self, user_id, candidate_videos, content_weight=0.6, collab_weight=0.4, top_n=10):
        """Combine content-based and collaborative filtering"""
        # Get user's watch history
        user_interactions = get_user_interactions(user_id)
        watched_videos = [interaction['video_id'] for interaction in user_interactions 
                         if interaction['interaction_type'] == 'view']
        
        if not watched_videos:
            # If no watch history, fall back to popular videos or random selection
            return self.popular_videos_recommendations(candidate_videos[:top_n])
        
        # Get content-based recommendations
        content_recs = self.content_based_recommendations(watched_videos, candidate_videos, top_n * 2)
        
        # Get collaborative filtering recommendations
        # For simplicity, we'll use a dummy dataset - in practice, this would come from database
        dummy_interactions = []
        for vid in watched_videos[:5]:  # Simulate some interactions
            dummy_interactions.append({'user_id': 'other_user_1', 'video_id': vid, 'interaction_type': 'view'})
            dummy_interactions.append({'user_id': 'other_user_2', 'video_id': vid, 'interaction_type': 'view'})
        
        collab_recs = self.collaborative_filtering_recommendations(
            user_id, dummy_interactions, candidate_videos, top_n * 2
        )
        
        # Combine recommendations using weighted average
        final_scores = defaultdict(float)
        
        # Add content-based scores
        for rec in content_recs:
            final_scores[rec['video_id']] += rec['score'] * content_weight
        
        # Add collaborative filtering scores
        for rec in collab_recs:
            final_scores[rec['video_id']] += rec['score'] * collab_weight
        
        # Sort by final score
        recommendations = []
        for video_id, score in sorted(final_scores.items(), key=lambda x: x[1], reverse=True)[:top_n]:
            recommendations.append({
                'video_id': video_id,
                'score': float(score),
                'type': 'hybrid'
            })
        
        return recommendations
    
    def popular_videos_recommendations(self, video_ids, top_n=10):
        """Recommend popular videos as fallback"""
        recommendations = []
        for video_id in video_ids[:top_n]:
            recommendations.append({
                'video_id': video_id,
                'score': 1.0,
                'type': 'popular'
            })
        return recommendations

# Global recommender instance
recommender = HybridRecommender()

def get_recommendations(user_id, limit=10):
    """Get hybrid recommendations for a user"""
    # For now, we'll use a dummy list of candidate videos
    # In practice, this would come from database or recent popular videos
    candidate_videos = [
        'dQw4w9WgXcQ',  # Rick Astley - Never Gonna Give You Up
        'jNQXAC9IVRw',  # Me at the zoo
        '9bZkp7q19f0',  # PSY - GANGNAM STYLE
        'kJQP7kiw5Fk',  # Luis Fonsi - Despacito
        'CevxZvSJLk8',  # Kony 2012
        'OPf0YbXqDm0',  # Mark Ronson - Uptown Funk
        '09R8_2nJtjg',  # Maroon 5 - Sugar
        'uelHwf8o7_U',  # Eminem - Love The Way You Lie
        'QK8mJJJvaes',  # Justin Bieber - Baby
        '2vjPBrBU-TM'   # Sia - Chandelier
    ]
    
    try:
        recommendations = recommender.hybrid_recommendations(user_id, candidate_videos, top_n=limit)
        
        # Enrich recommendations with video metadata
        enriched_recs = []
        for rec in recommendations:
            video_data = get_video_metadata(rec['video_id'])
            if not video_data:
                # Fetch from YouTube API if not in database
                try:
                    video_data = get_video_details(rec['video_id'])
                    if video_data:
                        save_video_metadata(video_data)
                except:
                    continue
            
            if video_data:
                enriched_rec = {
                    'video_id': rec['video_id'],
                    'title': video_data.get('title', ''),
                    'channel_title': video_data.get('channel_title', ''),
                    'thumbnail': video_data.get('thumbnail', ''),
                    'view_count': video_data.get('view_count', 0),
                    'score': rec['score'],
                    'type': rec['type']
                }
                enriched_recs.append(enriched_rec)
        
        return enriched_recs
        
    except Exception as e:
        raise Exception(f"Error generating recommendations: {str(e)}")

# Initialize the recommender when module is imported
def init_recommender():
    """Initialize recommender with some baseline data"""
    pass

init_recommender()
