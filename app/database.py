import os
from sqlalchemy import create_engine, Column, Integer, String, DateTime, Text, Float
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from datetime import datetime
import json

Base = declarative_base()

class User(Base):
    __tablename__ = 'users'
    
    id = Column(Integer, primary_key=True)
    user_id = Column(String(100), unique=True, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    preferences = Column(Text)  # JSON string for user preferences

class Video(Base):
    __tablename__ = 'videos'
    
    id = Column(Integer, primary_key=True)
    video_id = Column(String(50), unique=True, nullable=False)
    title = Column(String(500))
    description = Column(Text)
    channel_title = Column(String(200))
    tags = Column(Text)  # JSON string of tags
    category = Column(String(100))
    view_count = Column(Integer, default=0)
    like_count = Column(Integer, default=0)
    duration = Column(String(50))
    published_at = Column(DateTime)
    created_at = Column(DateTime, default=datetime.utcnow)

class WatchHistory(Base):
    __tablename__ = 'watch_history'
    
    id = Column(Integer, primary_key=True)
    user_id = Column(String(100), nullable=False)
    video_id = Column(String(50), nullable=False)
    watched_at = Column(DateTime, default=datetime.utcnow)
    watch_duration = Column(Integer)  # seconds watched
    rating = Column(Float)  # 0-5 rating

class UserVideoInteraction(Base):
    __tablename__ = 'user_video_interactions'
    
    id = Column(Integer, primary_key=True)
    user_id = Column(String(100), nullable=False)
    video_id = Column(String(50), nullable=False)
    interaction_type = Column(String(50))  # 'view', 'like', 'dislike', 'share'
    timestamp = Column(DateTime, default=datetime.utcnow)
    weight = Column(Float, default=1.0)  # interaction weight

# Database setup
DATABASE_URL = os.getenv('DATABASE_URL', 'sqlite:///youtube_recommender.db')
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def init_db():
    """Initialize database tables"""
    Base.metadata.create_all(bind=engine)

def get_db():
    """Get database session"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def add_watch_history(user_id, video_id, watch_duration=None, rating=None):
    """Add video to user's watch history"""
    db = SessionLocal()
    try:
        history_entry = WatchHistory(
            user_id=user_id,
            video_id=video_id,
            watch_duration=watch_duration,
            rating=rating
        )
        db.add(history_entry)
        db.commit()
        return history_entry
    except Exception as e:
        db.rollback()
        raise e
    finally:
        db.close()

def get_watch_history(user_id, limit=20):
    """Get user's watch history"""
    db = SessionLocal()
    try:
        history = db.query(WatchHistory)\
                   .filter(WatchHistory.user_id == user_id)\
                   .order_by(WatchHistory.watched_at.desc())\
                   .limit(limit)\
                   .all()
        return [{
            'video_id': h.video_id,
            'watched_at': h.watched_at.isoformat(),
            'watch_duration': h.watch_duration,
            'rating': h.rating
        } for h in history]
    finally:
        db.close()

def add_user_video_interaction(user_id, video_id, interaction_type, weight=1.0):
    """Add user-video interaction"""
    db = SessionLocal()
    try:
        interaction = UserVideoInteraction(
            user_id=user_id,
            video_id=video_id,
            interaction_type=interaction_type,
            weight=weight
        )
        db.add(interaction)
        db.commit()
        return interaction
    except Exception as e:
        db.rollback()
        raise e
    finally:
        db.close()

def get_user_interactions(user_id, limit=100):
    """Get user's interactions"""
    db = SessionLocal()
    try:
        interactions = db.query(UserVideoInteraction)\
                        .filter(UserVideoInteraction.user_id == user_id)\
                        .order_by(UserVideoInteraction.timestamp.desc())\
                        .limit(limit)\
                        .all()
        return [{
            'video_id': i.video_id,
            'interaction_type': i.interaction_type,
            'timestamp': i.timestamp.isoformat(),
            'weight': i.weight
        } for i in interactions]
    finally:
        db.close()

def save_video_metadata(video_data):
    """Save video metadata to database"""
    db = SessionLocal()
    try:
        # Check if video already exists
        existing = db.query(Video).filter(Video.video_id == video_data['id']).first()
        if existing:
            return existing
            
        video = Video(
            video_id=video_data['id'],
            title=video_data.get('title', ''),
            description=video_data.get('description', ''),
            channel_title=video_data.get('channel_title', ''),
            tags=json.dumps(video_data.get('tags', [])),
            view_count=video_data.get('view_count', 0),
            like_count=video_data.get('like_count', 0),
            duration=video_data.get('duration', ''),
            published_at=datetime.fromisoformat(video_data['published_at'].replace('Z', '+00:00')) if video_data.get('published_at') else None
        )
        db.add(video)
        db.commit()
        db.refresh(video)
        return video
    except Exception as e:
        db.rollback()
        raise e
    finally:
        db.close()

def get_video_metadata(video_id):
    """Get video metadata from database"""
    db = SessionLocal()
    try:
        video = db.query(Video).filter(Video.video_id == video_id).first()
        if video:
            return {
                'id': video.video_id,
                'title': video.title,
                'description': video.description,
                'channel_title': video.channel_title,
                'tags': json.loads(video.tags) if video.tags else [],
                'view_count': video.view_count,
                'like_count': video.like_count,
                'duration': video.duration,
                'published_at': video.published_at.isoformat() if video.published_at else None
            }
        return None
    finally:
        db.close()
