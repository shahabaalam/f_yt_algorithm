# Personal YouTube Recommendation System

A machine learning-powered YouTube recommendation system that provides personalized video suggestions based on your viewing history and preferences.

## Features

- **Hybrid Recommendation Engine**: Combines content-based and collaborative filtering
- **Video Search**: Search for YouTube videos directly through the interface
- **Watch History Tracking**: Automatically tracks videos you watch
- **Personalized Recommendations**: Smart suggestions based on your viewing patterns
- **Modern Web Interface**: Clean, responsive UI built with Bootstrap

## Technology Stack

- **Backend**: Python, Flask
- **Frontend**: HTML, CSS, JavaScript with Bootstrap
- **Database**: SQLite (with SQLAlchemy ORM)
- **Machine Learning**: Scikit-learn, Pandas, NumPy
- **YouTube Integration**: YouTube Data API v3

## Prerequisites

- Python 3.8+
- YouTube Data API Key
- pip (Python package manager)

## Installation

1. **Clone the repository:**
   ```bash
   git clone <repository-url>
   cd youtube-recommender
   ```

2. **Create a virtual environment:**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Set up environment variables:**
   ```bash
   cp .env.example .env
   ```
   Edit the `.env` file and add your YouTube API key:
   ```
   YOUTUBE_API_KEY=your_actual_api_key_here
   ```

5. **Run the application:**
   ```bash
   python app/main.py
   ```

6. **Access the application:**
   Open your browser and navigate to `http://localhost:5000`

## How It Works

### Recommendation Algorithm

The system uses a hybrid approach combining:

1. **Content-Based Filtering**: Analyzes video metadata (title, description, tags) using TF-IDF vectorization and cosine similarity
2. **Collaborative Filtering**: Finds similar users based on viewing patterns (simplified implementation)
3. **Hybrid Ranking**: Combines both approaches with weighted scoring

### Data Flow

1. User searches for videos → YouTube API fetches results
2. System stores video metadata and user interactions
3. ML model processes data to generate personalized recommendations
4. Recommendations served through web interface

## API Endpoints

- `GET /api/search?q={query}` - Search for videos
- `GET /api/recommendations?user_id={id}` - Get personalized recommendations
- `POST /api/watch_history` - Add video to watch history
- `GET /api/watch_history?user_id={id}` - Get watch history

## Project Structure

```
youtube-recommender/
├── app/
│   ├── __init__.py
│   ├── main.py          # Application entry point
│   ├── routes.py        # API routes
│   ├── youtube_api.py   # YouTube API integration
│   ├── database.py      # Database models and operations
│   ├── recommendations.py # ML recommendation engine
│   └── templates/
│       └── index.html   # Main web interface
├── requirements.txt     # Python dependencies
├── .env.example        # Environment variables template
└── README.md           # This file
```

## Usage

1. **Search for Videos**: Use the search bar to find videos of interest
2. **Watch Videos**: Click on any video card to watch it on YouTube (opens in new tab)
3. **View Recommendations**: See personalized suggestions on the main page
4. **Build History**: The more videos you watch, the better recommendations become

## Machine Learning Details

### Content-Based Filtering
- Uses TF-IDF vectorization on video text features
- Calculates cosine similarity between videos
- Considers title, description, tags, and channel information

### Collaborative Filtering
- User-based collaborative filtering (simplified)
- Jaccard similarity for user similarity calculation
- Weighted scoring based on similar users' preferences

### Hybrid Approach
- Combines both methods with configurable weights
- Content-based weight: 60%
- Collaborative filtering weight: 40%

## Future Enhancements

- [ ] Advanced deep learning models
- [ ] User rating system
- [ ] Real-time recommendation updates
- [ ] Video category preferences
- [ ] Time-based recommendation filtering
- [ ] Social features and sharing

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Submit a pull request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgments

- YouTube Data API for video data
- Scikit-learn for machine learning algorithms
- Bootstrap for responsive UI components
