// YouTube-inspired App JavaScript
class YouTubeApp {
    constructor() {
        this.USER_ID = 'default_user';
        this.sidebarVisible = false;
        this.currentVideoId = null;
        this.init();
    }

    init() {
        this.cacheDOM();
        this.bindEvents();
        this.loadInitialData();
        this.setupResponsive();
    }

    cacheDOM() {
        // Header elements
        this.menuIcon = document.querySelector('.menu-icon');
        this.searchInput = document.querySelector('.search-input');
        this.searchButton = document.querySelector('.search-button');
        
        // Sidebar elements
        this.sidebar = document.querySelector('.sidebar');
        
        // Content containers
        this.recommendationsContainer = document.getElementById('recommendationsContainer');
        this.searchResultsContainer = document.getElementById('searchResultsContainer');
        this.historyContainer = document.getElementById('historyContainer');
        
        // Modal elements
        this.videoModal = document.querySelector('.video-modal');
        this.closeModal = document.querySelector('.close-modal');
        this.videoModalTitle = document.querySelector('.video-modal-title');
        this.videoModalBody = document.querySelector('.video-modal-body');
    }

    bindEvents() {
        // Header events
        if (this.menuIcon) {
            this.menuIcon.addEventListener('click', () => this.toggleSidebar());
        }
        
        if (this.searchButton) {
            this.searchButton.addEventListener('click', () => this.performSearch());
        }
        
        if (this.searchInput) {
            this.searchInput.addEventListener('keypress', (e) => {
                if (e.key === 'Enter') {
                    this.performSearch();
                }
            });
        }
        
        // Modal events
        if (this.closeModal) {
            this.closeModal.addEventListener('click', () => this.closeVideoModal());
        }
        
        if (this.videoModal) {
            this.videoModal.addEventListener('click', (e) => {
                if (e.target === this.videoModal) {
                    this.closeVideoModal();
                }
            });
        }
        
        // Sidebar item clicks
        const sidebarItems = document.querySelectorAll('.sidebar-item');
        sidebarItems.forEach(item => {
            item.addEventListener('click', () => this.handleSidebarItemClick(item));
        });
        
        // Window resize for responsive design
        window.addEventListener('resize', () => this.setupResponsive());
    }

    setupResponsive() {
        const width = window.innerWidth;
        if (width > 992) {
            this.sidebarVisible = true;
            if (this.sidebar) {
                this.sidebar.classList.add('visible');
            }
        } else {
            this.sidebarVisible = false;
            if (this.sidebar) {
                this.sidebar.classList.remove('visible');
            }
        }
    }

    toggleSidebar() {
        this.sidebarVisible = !this.sidebarVisible;
        if (this.sidebar) {
            this.sidebar.classList.toggle('visible', this.sidebarVisible);
        }
    }

    handleSidebarItemClick(item) {
        // Remove active class from all items
        document.querySelectorAll('.sidebar-item').forEach(i => {
            i.classList.remove('active');
        });
        
        // Add active class to clicked item
        item.classList.add('active');
        
        // Handle specific item actions
        const action = item.dataset.action;
        switch (action) {
            case 'home':
                this.loadRecommendations();
                break;
            case 'history':
                this.loadWatchHistory();
                break;
            case 'trending':
                this.loadTrending();
                break;
        }
    }

    async performSearch() {
        const query = this.searchInput ? this.searchInput.value.trim() : '';
        if (!query) return;

        this.showLoading(this.searchResultsContainer);

        try {
            const response = await fetch(`/api/search?q=${encodeURIComponent(query)}&max_results=12`);
            const data = await response.json();

            if (data.videos && data.videos.length > 0) {
                this.displayVideos(data.videos, this.searchResultsContainer, 'search');
            } else {
                this.showEmptyState(this.searchResultsContainer, 'No videos found for your search.');
            }
        } catch (error) {
            this.showError(this.searchResultsContainer, 'Error loading search results');
            console.error('Search error:', error);
        }
    }

    async loadRecommendations() {
        this.showLoading(this.recommendationsContainer);

        try {
            const response = await fetch(`/api/recommendations?user_id=${this.USER_ID}&limit=12`);
            const data = await response.json();

            if (data.recommendations && data.recommendations.length > 0) {
                this.displayVideos(data.recommendations, this.recommendationsContainer, 'recommendation');
            } else {
                this.showEmptyState(this.recommendationsContainer, 'No recommendations yet. Start watching videos to get personalized suggestions!');
            }
        } catch (error) {
            this.showError(this.recommendationsContainer, 'Error loading recommendations');
            console.error('Recommendations error:', error);
        }
    }

    async loadWatchHistory() {
        this.showLoading(this.historyContainer);

        try {
            const response = await fetch(`/api/watch_history?user_id=${this.USER_ID}&limit=6`);
            const data = await response.json();

            if (data.history && data.history.length > 0) {
                // For now, we'll just show a message. In a real app, we'd fetch video details
                this.showEmptyState(this.historyContainer, 'Watch history will appear here after you watch videos');
            } else {
                this.showEmptyState(this.historyContainer, 'No watch history yet');
            }
        } catch (error) {
            this.showError(this.historyContainer, 'Error loading watch history');
            console.error('History error:', error);
        }
    }

    async loadTrending() {
        this.showLoading(this.searchResultsContainer);
        this.showSectionHeader('Trending Videos');

        try {
            const response = await fetch(`/api/search?q=trending&max_results=12`);
            const data = await response.json();

            if (data.videos && data.videos.length > 0) {
                this.displayVideos(data.videos, this.searchResultsContainer, 'trending');
            } else {
                this.showEmptyState(this.searchResultsContainer, 'No trending videos available.');
            }
        } catch (error) {
            this.showError(this.searchResultsContainer, 'Error loading trending videos');
            console.error('Trending error:', error);
        }
    }

    async addToWatchHistory(videoId) {
        try {
            await fetch('/api/watch_history', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    user_id: this.USER_ID,
                    video_id: videoId
                })
            });
        } catch (error) {
            console.error('Error adding to watch history:', error);
        }
    }

    displayVideos(videos, container, type = 'search') {
        if (!container) return;

        if (videos.length === 0) {
            this.showEmptyState(container, 'No videos found');
            return;
        }

        const videoGrid = document.createElement('div');
        videoGrid.className = 'video-grid';

        videoGrid.innerHTML = videos.map(video => this.createVideoCard(video, type)).join('');

        container.innerHTML = '';
        container.appendChild(videoGrid);

        // Add click event listeners
        container.querySelectorAll('.video-card').forEach(card => {
            card.addEventListener('click', () => {
                const videoId = card.dataset.videoId;
                this.openVideo(videoId, video.title);
            });
        });
    }

    createVideoCard(video, type) {
        const isRecommendation = type === 'recommendation';
        const duration = this.formatDuration(video.duration || 'PT5M30S');
        const viewCount = this.formatNumber(video.view_count || 0);
        const publishDate = this.formatDate(video.published_at || new Date());

        return `
            <div class="video-card" data-video-id="${video.video_id}">
                <div class="video-thumbnail">
                    <img src="${video.thumbnail}" alt="${video.title}" loading="lazy">
                    <div class="video-duration">${duration}</div>
                    ${isRecommendation ? '<div class="recommendation-badge">Recommended</div>' : ''}
                </div>
                <div class="video-info">
                    <h3 class="video-title" title="${video.title}">${video.title}</h3>
                    <p class="video-channel">${video.channel_title}</p>
                    <p class="video-stats">
                        ${viewCount} views • ${publishDate}
                        ${isRecommendation ? `<br><span class="video-score">Score: ${video.score ? video.score.toFixed(2) : 'N/A'}</span>` : ''}
                    </p>
                </div>
            </div>
        `;
    }

    formatDuration(duration) {
        // Simple duration formatting (you might want to enhance this)
        if (!duration) return '5:30';
        
        // Extract minutes and seconds from ISO 8601 duration format
        const match = duration.match(/PT(\d+M)?(\d+S)?/);
        if (match) {
            const minutes = match[1] ? parseInt(match[1]) : 5;
            const seconds = match[2] ? parseInt(match[2]) : 30;
            return `${minutes}:${seconds.toString().padStart(2, '0')}`;
        }
        return '5:30';
    }

    formatNumber(num) {
        if (num >= 1000000) {
            return (num / 1000000).toFixed(1) + 'M';
        } else if (num >= 1000) {
            return (num / 1000).toFixed(1) + 'K';
        }
        return num.toString();
    }

    formatDate(dateString) {
        const date = new Date(dateString);
        const now = new Date();
        const diffTime = Math.abs(now - date);
        const diffDays = Math.ceil(diffTime / (1000 * 60 * 60 * 24));
        
        if (diffDays === 1) {
            return '1 day ago';
        } else if (diffDays < 7) {
            return `${diffDays} days ago`;
        } else if (diffDays < 30) {
            const weeks = Math.floor(diffDays / 7);
            return `${weeks} week${weeks > 1 ? 's' : ''} ago`;
        } else {
            const months = Math.floor(diffDays / 30);
            return `${months} month${months > 1 ? 's' : ''} ago`;
        }
    }

    openVideo(videoId, title) {
        this.currentVideoId = videoId;
        
        // Add to watch history
        this.addToWatchHistory(videoId);
        
        // Show modal with embedded player
        if (this.videoModal && this.videoModalBody) {
            this.videoModalTitle.textContent = title || 'Video Player';
            this.videoModalBody.innerHTML = `
                <iframe 
                    src="https://www.youtube.com/embed/${videoId}?autoplay=1" 
                    allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture" 
                    allowfullscreen>
                </iframe>
            `;
            this.videoModal.style.display = 'flex';
            
            // Refresh recommendations after watching
            setTimeout(() => {
                this.loadRecommendations();
            }, 2000);
        } else {
            // Fallback to opening in new tab
            window.open(`https://www.youtube.com/watch?v=${videoId}`, '_blank');
        }
    }

    closeVideoModal() {
        if (this.videoModal) {
            this.videoModal.style.display = 'none';
            this.videoModalBody.innerHTML = '';
            this.currentVideoId = null;
        }
    }

    showLoading(container) {
        if (!container) return;
        
        container.innerHTML = `
            <div class="video-grid">
                ${Array(6).fill().map(() => `
                    <div class="skeleton-card">
                        <div class="skeleton-thumbnail"></div>
                        <div class="skeleton-text">
                            <div class="skeleton-title"></div>
                            <div class="skeleton-channel"></div>
                            <div class="skeleton-stats"></div>
                        </div>
                    </div>
                `).join('')}
            </div>
        `;
    }

    showEmptyState(container, message) {
        if (!container) return;
        
        container.innerHTML = `
            <div class="text-center text-muted" style="padding: 40px 0;">
                <p>${message}</p>
            </div>
        `;
    }

    showError(container, message) {
        if (!container) return;
        
        container.innerHTML = `
            <div class="text-center text-danger" style="padding: 40px 0;">
                <p>${message}</p>
            </div>
        `;
    }

    showSectionHeader(title) {
        const header = document.querySelector('.search-results-header');
        if (header) {
            header.innerHTML = `
                <div class="section-header">
                    <h3><i class="fas fa-fire"></i> ${title}</h3>
                </div>
            `;
        }
    }

    loadInitialData() {
        // Load recommendations on page load
        setTimeout(() => {
            this.loadRecommendations();
            this.loadWatchHistory();
        }, 100);
    }
}

// Initialize the app when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    window.youtubeApp = new YouTubeApp();
});

// Utility function for formatting numbers (global access)
window.formatNumber = function(num) {
    if (num >= 1000000) {
        return (num / 1000000).toFixed(1) + 'M';
    } else if (num >= 1000) {
        return (num / 1000).toFixed(1) + 'K';
    }
    return num.toString();
};
