"""
Analytics tracking and reporting utilities.
"""

import logging
from typing import Dict, Any, Optional
from datetime import datetime, timedelta
from collections import defaultdict


logger = logging.getLogger(__name__)


class AnalyticsTracker:
    """Tracks and reports analytics for posts."""
    
    def __init__(self):
        """Initialize analytics tracker."""
        self.post_analytics: Dict[str, Dict[str, Any]] = {}
        self.platform_stats: Dict[str, Dict[str, int]] = defaultdict(
            lambda: {'posts': 0, 'success': 0, 'failed': 0}
        )
    
    def track_post(self, post):
        """
        Track analytics for a post.
        
        Args:
            post: Post object
        """
        self.post_analytics[post.post_id] = {
            'platforms': post.platforms,
            'status': post.status.value,
            'created_at': post.created_at,
            'platform_results': post.platform_results
        }
        
        # Update platform stats
        for platform in post.platforms:
            self.platform_stats[platform]['posts'] += 1
            
            if platform in post.platform_results:
                result = post.platform_results[platform]['result']
                if result == 'success':
                    self.platform_stats[platform]['success'] += 1
                elif result == 'failed':
                    self.platform_stats[platform]['failed'] += 1
        
        logger.info(f"Analytics tracked for post: {post.post_id}")
    
    def get_post_analytics(self, post) -> Dict[str, Any]:
        """
        Get analytics for a specific post.
        
        Args:
            post: Post object
            
        Returns:
            Analytics dictionary
        """
        if post.post_id not in self.post_analytics:
            return {}
        
        return self.post_analytics[post.post_id]
    
    def get_platform_stats(self, platform: Optional[str] = None) -> Dict[str, Any]:
        """
        Get platform statistics.
        
        Args:
            platform: Optional specific platform
            
        Returns:
            Platform statistics
        """
        if platform:
            return dict(self.platform_stats.get(platform, {}))
        
        return dict(self.platform_stats)
    
    def get_range_analytics(
        self,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None
    ) -> Dict[str, Any]:
        """
        Get analytics for a date range.
        
        Args:
            start_date: Start date
            end_date: End date
            
        Returns:
            Analytics for range
        """
        if not start_date:
            start_date = datetime.now() - timedelta(days=7)
        if not end_date:
            end_date = datetime.now()
        
        total_posts = 0
        successful_posts = 0
        failed_posts = 0
        
        for post_id, analytics in self.post_analytics.items():
            created_at = analytics.get('created_at')
            if start_date <= created_at <= end_date:
                total_posts += 1
                status = analytics.get('status')
                if status == 'published':
                    successful_posts += 1
                elif status == 'failed':
                    failed_posts += 1
        
        return {
            'period': {
                'start': start_date.isoformat(),
                'end': end_date.isoformat()
            },
            'total_posts': total_posts,
            'successful_posts': successful_posts,
            'failed_posts': failed_posts,
            'success_rate': (successful_posts / total_posts * 100) if total_posts > 0 else 0,
            'platform_stats': self.get_platform_stats()
        }
    
    def get_summary(self) -> Dict[str, Any]:
        """Get overall analytics summary."""
        total = len(self.post_analytics)
        
        return {
            'total_posts_tracked': total,
            'platforms': len(self.platform_stats),
            'platform_stats': dict(self.platform_stats)
        }
