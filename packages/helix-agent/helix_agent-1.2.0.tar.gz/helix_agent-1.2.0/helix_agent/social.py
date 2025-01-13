import tweepy
from typing import List, Dict, Any, Optional
from datetime import datetime

class SocialMediaTools:
    """Tools for social media integration with HelixAgent."""
    
    def __init__(self, twitter_config: Optional[Dict[str, str]] = None):
        """
        Initialize social media tools.
        
        Parameters:
            twitter_config (dict): Twitter API credentials containing:
                - api_key
                - api_secret
                - access_token
                - access_token_secret
        """
        self.twitter_api = None
        if twitter_config:
            self.setup_twitter(twitter_config)
    
    def setup_twitter(self, config: Dict[str, str]) -> None:
        """Set up Twitter API client."""
        auth = tweepy.OAuthHandler(
            config['api_key'],
            config['api_secret']
        )
        auth.set_access_token(
            config['access_token'],
            config['access_token_secret']
        )
        self.twitter_api = tweepy.API(auth)
        
    def post_tweet(self, content: str, media_paths: Optional[List[str]] = None) -> Dict[str, Any]:
        """
        Post a tweet with optional media attachments.
        
        Parameters:
            content (str): Tweet text content
            media_paths (List[str], optional): Paths to media files to attach
            
        Returns:
            dict: Tweet metadata including id and timestamp
        """
        if not self.twitter_api:
            raise ValueError("Twitter API not configured. Call setup_twitter first.")
            
        media_ids = []
        if media_paths:
            for path in media_paths:
                media = self.twitter_api.media_upload(path)
                media_ids.append(media.media_id)
        
        tweet = self.twitter_api.update_status(
            status=content,
            media_ids=media_ids if media_ids else None
        )
        
        return {
            'id': tweet.id,
            'content': tweet.text,
            'created_at': tweet.created_at.isoformat(),
            'media_count': len(media_ids)
        }
        
    def get_tweet_history(self, count: int = 10) -> List[Dict[str, Any]]:
        """
        Get recent tweets from the account.
        
        Parameters:
            count (int): Number of tweets to retrieve
            
        Returns:
            List[dict]: List of tweet metadata
        """
        if not self.twitter_api:
            raise ValueError("Twitter API not configured. Call setup_twitter first.")
            
        tweets = self.twitter_api.user_timeline(count=count)
        return [{
            'id': tweet.id,
            'content': tweet.text,
            'created_at': tweet.created_at.isoformat(),
            'likes': tweet.favorite_count,
            'retweets': tweet.retweet_count
        } for tweet in tweets]
        
    def schedule_tweet(self, content: str, 
                      scheduled_time: datetime,
                      media_paths: Optional[List[str]] = None) -> Dict[str, Any]:
        """
        Schedule a tweet for future posting.
        
        Parameters:
            content (str): Tweet text content
            scheduled_time (datetime): When to post the tweet
            media_paths (List[str], optional): Paths to media files to attach
            
        Returns:
            dict: Scheduled tweet metadata
        """
        if not self.twitter_api:
            raise ValueError("Twitter API not configured. Call setup_twitter first.")
            
        # Store scheduled tweet info
        scheduled_tweet = {
            'content': content,
            'scheduled_time': scheduled_time.isoformat(),
            'media_paths': media_paths,
            'status': 'scheduled'
        }
        
        # Note: Actual scheduling would require additional infrastructure
        # like a task queue (e.g., Celery) or a cron job
        return scheduled_tweet
        
    def analyze_engagement(self, tweet_id: str) -> Dict[str, Any]:
        """
        Analyze engagement metrics for a specific tweet.
        
        Parameters:
            tweet_id (str): ID of the tweet to analyze
            
        Returns:
            dict: Engagement metrics
        """
        if not self.twitter_api:
            raise ValueError("Twitter API not configured. Call setup_twitter first.")
            
        tweet = self.twitter_api.get_status(tweet_id)
        
        return {
            'likes': tweet.favorite_count,
            'retweets': tweet.retweet_count,
            'replies': None,  # Requires elevated API access
            'impressions': None,  # Requires elevated API access
            'engagement_rate': None,  # Requires elevated API access
            'analyzed_at': datetime.now().isoformat()
        }
