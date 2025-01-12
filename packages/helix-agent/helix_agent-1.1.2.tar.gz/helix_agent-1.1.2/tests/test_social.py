import pytest
from unittest.mock import Mock, patch
from datetime import datetime
from helix_agent.social import SocialMediaTools

@pytest.fixture
def mock_twitter_api():
    with patch('tweepy.API') as mock_api:
        yield mock_api

@pytest.fixture
def social_tools():
    config = {
        'api_key': 'test_key',
        'api_secret': 'test_secret',
        'access_token': 'test_token',
        'access_token_secret': 'test_token_secret'
    }
    return SocialMediaTools(twitter_config=config)

def test_initialization_without_config():
    tools = SocialMediaTools()
    assert tools.twitter_api is None

def test_initialization_with_config():
    config = {
        'api_key': 'test_key',
        'api_secret': 'test_secret',
        'access_token': 'test_token',
        'access_token_secret': 'test_token_secret'
    }
    with patch('tweepy.OAuthHandler'), patch('tweepy.API'):
        tools = SocialMediaTools(twitter_config=config)
        assert tools.twitter_api is not None

def test_post_tweet_without_media(social_tools, mock_twitter_api):
    # Mock tweet response
    mock_tweet = Mock()
    mock_tweet.id = '12345'
    mock_tweet.text = 'Test tweet'
    mock_tweet.created_at = datetime.now()
    
    mock_twitter_api.return_value.update_status.return_value = mock_tweet
    social_tools.twitter_api = mock_twitter_api.return_value
    
    result = social_tools.post_tweet("Test tweet")
    
    assert result['id'] == '12345'
    assert result['content'] == 'Test tweet'
    assert 'created_at' in result
    assert result['media_count'] == 0

def test_post_tweet_with_media(social_tools, mock_twitter_api):
    # Mock media upload
    mock_media = Mock()
    mock_media.media_id = 'media123'
    
    # Mock tweet response
    mock_tweet = Mock()
    mock_tweet.id = '12345'
    mock_tweet.text = 'Test tweet with media'
    mock_tweet.created_at = datetime.now()
    
    mock_twitter_api.return_value.media_upload.return_value = mock_media
    mock_twitter_api.return_value.update_status.return_value = mock_tweet
    social_tools.twitter_api = mock_twitter_api.return_value
    
    result = social_tools.post_tweet(
        "Test tweet with media",
        media_paths=["image.jpg"]
    )
    
    assert result['id'] == '12345'
    assert result['content'] == 'Test tweet with media'
    assert result['media_count'] == 1

def test_get_tweet_history(social_tools, mock_twitter_api):
    # Mock timeline tweets
    mock_tweet1 = Mock()
    mock_tweet1.id = '12345'
    mock_tweet1.text = 'Tweet 1'
    mock_tweet1.created_at = datetime.now()
    mock_tweet1.favorite_count = 10
    mock_tweet1.retweet_count = 5
    
    mock_tweet2 = Mock()
    mock_tweet2.id = '67890'
    mock_tweet2.text = 'Tweet 2'
    mock_tweet2.created_at = datetime.now()
    mock_tweet2.favorite_count = 20
    mock_tweet2.retweet_count = 8
    
    mock_twitter_api.return_value.user_timeline.return_value = [mock_tweet1, mock_tweet2]
    social_tools.twitter_api = mock_twitter_api.return_value
    
    tweets = social_tools.get_tweet_history(count=2)
    
    assert len(tweets) == 2
    assert tweets[0]['id'] == '12345'
    assert tweets[0]['content'] == 'Tweet 1'
    assert tweets[0]['likes'] == 10
    assert tweets[0]['retweets'] == 5
    assert tweets[1]['id'] == '67890'
    assert tweets[1]['content'] == 'Tweet 2'
    assert tweets[1]['likes'] == 20
    assert tweets[1]['retweets'] == 8

def test_schedule_tweet(social_tools):
    scheduled_time = datetime.now()
    result = social_tools.schedule_tweet(
        "Scheduled tweet",
        scheduled_time,
        media_paths=["image.jpg"]
    )
    
    assert result['content'] == "Scheduled tweet"
    assert result['scheduled_time'] == scheduled_time.isoformat()
    assert result['media_paths'] == ["image.jpg"]
    assert result['status'] == 'scheduled'

def test_analyze_engagement(social_tools, mock_twitter_api):
    # Mock tweet response
    mock_tweet = Mock()
    mock_tweet.favorite_count = 100
    mock_tweet.retweet_count = 50
    
    mock_twitter_api.return_value.get_status.return_value = mock_tweet
    social_tools.twitter_api = mock_twitter_api.return_value
    
    metrics = social_tools.analyze_engagement("12345")
    
    assert metrics['likes'] == 100
    assert metrics['retweets'] == 50
    assert 'analyzed_at' in metrics
    # These require elevated API access
    assert metrics['replies'] is None
    assert metrics['impressions'] is None
    assert metrics['engagement_rate'] is None

def test_post_tweet_without_api():
    tools = SocialMediaTools()  # No config provided
    with pytest.raises(ValueError, match="Twitter API not configured"):
        tools.post_tweet("Test tweet")

def test_get_tweet_history_without_api():
    tools = SocialMediaTools()  # No config provided
    with pytest.raises(ValueError, match="Twitter API not configured"):
        tools.get_tweet_history()

def test_analyze_engagement_without_api():
    tools = SocialMediaTools()  # No config provided
    with pytest.raises(ValueError, match="Twitter API not configured"):
        tools.analyze_engagement("12345")
