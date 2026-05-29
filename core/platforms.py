"""
Platform abstraction layer for multi-platform social media posting.
Handles communication with different social media APIs.
"""

import logging
import os
from typing import Dict, Optional, Any
from abc import ABC, abstractmethod

import tweepy
import requests


logger = logging.getLogger(__name__)


class PlatformConnector(ABC):
    """Abstract base class for platform connectors."""
    
    @abstractmethod
    def post(self, content: str, media: list = None, metadata: dict = None) -> bool:
        """Post content to platform."""
        pass
    
    @abstractmethod
    def delete(self, post_id: str) -> bool:
        """Delete a post from platform."""
        pass
    
    @abstractmethod
    def get_analytics(self, post_id: str) -> dict:
        """Get analytics for a post."""
        pass


class TwitterConnector(PlatformConnector):
    """Twitter/X connector."""
    
    def __init__(self, api_key: str, api_secret: str, access_token: str, access_secret: str):
        """Initialize Twitter connector."""
        self.auth = tweepy.OAuthHandler(api_key, api_secret)
        self.auth.set_access_token(access_token, access_secret)
        self.api = tweepy.API(self.auth)
        self.client = tweepy.Client(
            consumer_key=api_key,
            consumer_secret=api_secret,
            access_token=access_token,
            access_token_secret=access_secret
        )
    
    def post(self, content: str, media: list = None, metadata: dict = None) -> bool:
        """Post to Twitter."""
        try:
            # Handle media
            media_ids = []
            if media:
                for media_file in media:
                    uploaded = self.api.media_upload(media_file)
                    media_ids.append(uploaded.media_id)
            
            # Post tweet
            response = self.client.create_tweet(
                text=content[:280],  # Twitter character limit
                media_ids=media_ids if media_ids else None
            )
            logger.info(f"Posted to Twitter: {response.data['id']}")
            return True
        except Exception as e:
            logger.error(f"Twitter posting error: {str(e)}")
            return False
    
    def delete(self, post_id: str) -> bool:
        """Delete tweet."""
        try:
            self.client.delete_tweet(id=post_id)
            logger.info(f"Deleted tweet: {post_id}")
            return True
        except Exception as e:
            logger.error(f"Twitter deletion error: {str(e)}")
            return False
    
    def get_analytics(self, post_id: str) -> dict:
        """Get tweet analytics."""
        try:
            tweet = self.client.get_tweet(id=post_id, tweet_fields=['public_metrics'])
            metrics = tweet.data['public_metrics']
            return {
                'likes': metrics['like_count'],
                'retweets': metrics['retweet_count'],
                'replies': metrics['reply_count']
            }
        except Exception as e:
            logger.error(f"Twitter analytics error: {str(e)}")
            return {}


class FacebookConnector(PlatformConnector):
    """Facebook connector."""
    
    def __init__(self, access_token: str, page_id: str):
        """Initialize Facebook connector."""
        self.access_token = access_token
        self.page_id = page_id
        self.base_url = "https://graph.facebook.com/v18.0"
    
    def post(self, content: str, media: list = None, metadata: dict = None) -> bool:
        """Post to Facebook."""
        try:
            url = f"{self.base_url}/{self.page_id}/feed"
            
            if media:
                # Post with image
                with open(media[0], 'rb') as f:
                    files = {'source': f}
                    data = {
                        'message': content,
                        'access_token': self.access_token
                    }
                    response = requests.post(url, data=data, files=files)
            else:
                # Post text only
                data = {
                    'message': content,
                    'access_token': self.access_token
                }
                response = requests.post(url, data=data)
            
            if response.status_code == 200:
                logger.info(f"Posted to Facebook: {response.json()['id']}")
                return True
            else:
                logger.error(f"Facebook error: {response.text}")
                return False
        except Exception as e:
            logger.error(f"Facebook posting error: {str(e)}")
            return False
    
    def delete(self, post_id: str) -> bool:
        """Delete Facebook post."""
        try:
            url = f"{self.base_url}/{post_id}"
            params = {'access_token': self.access_token}
            response = requests.delete(url, params=params)
            
            if response.status_code == 200:
                logger.info(f"Deleted Facebook post: {post_id}")
                return True
            return False
        except Exception as e:
            logger.error(f"Facebook deletion error: {str(e)}")
            return False
    
    def get_analytics(self, post_id: str) -> dict:
        """Get Facebook post analytics."""
        try:
            url = f"{self.base_url}/{post_id}"
            params = {
                'fields': 'likes.summary(true),comments.summary(true),shares',
                'access_token': self.access_token
            }
            response = requests.get(url, params=params)
            
            if response.status_code == 200:
                data = response.json()
                return {
                    'likes': data['likes']['summary']['total_count'],
                    'comments': data['comments']['summary']['total_count'],
                    'shares': data.get('shares', {}).get('data', [])
                }
            return {}
        except Exception as e:
            logger.error(f"Facebook analytics error: {str(e)}")
            return {}


class LinkedInConnector(PlatformConnector):
    """LinkedIn connector."""
    
    def __init__(self, access_token: str):
        """Initialize LinkedIn connector."""
        self.access_token = access_token
        self.base_url = "https://api.linkedin.com/v2"
        self.headers = {
            'Authorization': f'Bearer {access_token}',
            'Content-Type': 'application/json'
        }
    
    def post(self, content: str, media: list = None, metadata: dict = None) -> bool:
        """Post to LinkedIn."""
        try:
            url = f"{self.base_url}/ugcPosts"
            
            payload = {
                'lifecycleState': 'PUBLISHED',
                'specificContent': {
                    'com.linkedin.ugc.ShareContent': {
                        'shareCommentary': {
                            'text': content
                        },
                        'shareMediaCategory': 'NONE'
                    }
                },
                'visibility': {
                    'com.linkedin.ugc.MemberNetworkVisibility': 'PUBLIC'
                }
            }
            
            response = requests.post(url, json=payload, headers=self.headers)
            
            if response.status_code == 201:
                logger.info(f"Posted to LinkedIn: {response.json()['id']}")
                return True
            else:
                logger.error(f"LinkedIn error: {response.text}")
                return False
        except Exception as e:
            logger.error(f"LinkedIn posting error: {str(e)}")
            return False
    
    def delete(self, post_id: str) -> bool:
        """Delete LinkedIn post."""
        try:
            url = f"{self.base_url}/ugcPosts/{post_id}"
            response = requests.delete(url, headers=self.headers)
            
            if response.status_code == 204:
                logger.info(f"Deleted LinkedIn post: {post_id}")
                return True
            return False
        except Exception as e:
            logger.error(f"LinkedIn deletion error: {str(e)}")
            return False
    
    def get_analytics(self, post_id: str) -> dict:
        """Get LinkedIn post analytics."""
        # LinkedIn analytics requires additional permissions
        return {'note': 'Analytics require advanced permissions'}


class PlatformManager:
    """Manages multiple platform connectors."""
    
    PLATFORM_MAP = {
        'twitter': TwitterConnector,
        'facebook': FacebookConnector,
        'linkedin': LinkedInConnector,
    }
    
    def __init__(self, config: Dict[str, Any] = None):
        """Initialize platform manager."""
        self.config = config or {}
        self.connectors: Dict[str, PlatformConnector] = {}
        self._initialize_connectors()
    
    def _initialize_connectors(self):
        """Initialize all configured connectors."""
        # Load from environment variables if not in config
        if 'twitter' not in self.connectors:
            api_key = os.getenv('TWITTER_API_KEY')
            api_secret = os.getenv('TWITTER_API_SECRET')
            access_token = os.getenv('TWITTER_ACCESS_TOKEN')
            access_secret = os.getenv('TWITTER_ACCESS_SECRET')
            
            if all([api_key, api_secret, access_token, access_secret]):
                self.connectors['twitter'] = TwitterConnector(
                    api_key, api_secret, access_token, access_secret
                )
        
        if 'facebook' not in self.connectors:
            access_token = os.getenv('FACEBOOK_ACCESS_TOKEN')
            page_id = os.getenv('FACEBOOK_PAGE_ID')
            
            if access_token and page_id:
                self.connectors['facebook'] = FacebookConnector(access_token, page_id)
        
        if 'linkedin' not in self.connectors:
            access_token = os.getenv('LINKEDIN_ACCESS_TOKEN')
            
            if access_token:
                self.connectors['linkedin'] = LinkedInConnector(access_token)
    
    def post(self, post, platform: str) -> bool:
        """
        Post to a specific platform.
        
        Args:
            post: Post object with content and media
            platform: Target platform name
            
        Returns:
            Success status
        """
        if platform not in self.connectors:
            logger.warning(f"Platform not configured: {platform}")
            return False
        
        connector = self.connectors[platform]
        return connector.post(post.content, post.media, post.metadata)
    
    def delete(self, platform: str, post_id: str) -> bool:
        """Delete post from platform."""
        if platform not in self.connectors:
            logger.warning(f"Platform not configured: {platform}")
            return False
        
        connector = self.connectors[platform]
        return connector.delete(post_id)
    
    def get_analytics(self, platform: str, post_id: str) -> dict:
        """Get analytics from platform."""
        if platform not in self.connectors:
            logger.warning(f"Platform not configured: {platform}")
            return {}
        
        connector = self.connectors[platform]
        return connector.get_analytics(post_id)
