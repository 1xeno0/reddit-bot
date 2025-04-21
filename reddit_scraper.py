import requests
from bs4 import BeautifulSoup
import json
from typing import Dict, Any, List
import logging
from datetime import datetime
import time
import os
import sqlite3
from pathlib import Path

class RedditScraper:
    def __init__(self, config_path: str):
        self.config = self._load_config(config_path)
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': self.config['reddit']['user_agent']
        })
        self._setup_logging()
        self._setup_directories()

    def _setup_logging(self):
        """Setup logging for the RedditScraper"""
        self.logger = logging.getLogger('RedditScraper')
        self.logger.setLevel(logging.INFO)
        
        # Add console handler
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.INFO)
        formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
        console_handler.setFormatter(formatter)
        self.logger.addHandler(console_handler)


    def _setup_directories(self):
        """Create necessary directories for storing JSON files"""
        self.base_dir = Path('story_configs')
        self.base_dir.mkdir(exist_ok=True)

    def _save_post_data(self, post_data: Dict[str, Any], i: int) -> bool:
        """
        Save post data to both JSON file and database
        
        Returns:
            bool: True if post was saved, False if it was already scraped
        """

        # Create a safe filename from the title
        safe_title = "".join(c for c in post_data['title'] if c.isalnum() or c in (' ', '-', '_')).rstrip()
        filename = f"{i}_{datetime.now().strftime('%Y-%H-%M-%m-%d-')}.json"
        filepath = self.base_dir / filename
        print(filepath)

        # Save JSON file
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(post_data, f, indent=2, ensure_ascii=False)

        self.logger.info(f"Saved new post: {post_data['title']}")
        return True

    def _load_config(self, config_path: str) -> Dict[str, Any]:
        """Load configuration from JSON file"""
        try:
            with open(config_path, 'r') as file:
                return json.load(file)
        except Exception as e:
            self.logger.error(f"Failed to load config file: {e}")
            raise

    def _get_post_content(self, post_url: str) -> str:
        """
        Fetch and extract the content from a Reddit post URL
        
        Args:
            post_url: URL of the Reddit post
            
        Returns:
            String containing the post content
        """
        try:
            # Convert the post URL to use the JSON API
            json_url = f"{post_url}.json"
            response = self.session.get(json_url)
            response.raise_for_status()
            
            # Parse the JSON response
            data = response.json()
            post_data = data[0]['data']['children'][0]['data']
            
            # Handle different types of posts
            if 'selftext' in post_data and post_data['selftext']:
                return post_data['selftext']
            elif 'url' in post_data and post_data['url']:
                return f"Link post: {post_data['url']}"
            else:
                return "No text content available"
                
        except Exception as e:
            self.logger.error(f"Error fetching post content from {post_url}: {e}")
            return "Error fetching post content"

    def get_posts_from_subreddit(self, subreddit: str) -> List[Dict[str, Any]]:
        """
        Get posts from a subreddit using Reddit's JSON API
        
        Args:
            subreddit: Name of the subreddit to scrape
            
        Returns:
            List of post dictionaries containing post details
        """
        try:
            url = f"https://www.reddit.com/r/{subreddit}/rising.json"
            self.logger.info(f"Fetching posts from r/{subreddit}")
            
            response = self.session.get(url)
            response.raise_for_status()
            
            data = response.json()
            posts = []
            
            # Extract posts from the JSON response
            for i, post in enumerate(data['data']['children']):
                post_data = post['data']
                post_url = f"https://reddit.com{post_data['permalink']}"
                
                # Get post content
                content = self._get_post_content(post_url)
                
                processed_post = {
                    'title': post_data['title'],
                    'url': post_url,
                    'subreddit': subreddit,
                    'timestamp': datetime.fromtimestamp(post_data['created_utc']).isoformat(),
                    'score': str(post_data['score']),
                    'author': post_data['author'],
                    'num_comments': str(post_data['num_comments']),
                    'content': content,
                    'scrape_date': datetime.now().isoformat()
                }
                
                # Save post data if it's new
                if self._save_post_data(processed_post, i):
                    posts.append(processed_post)
                    self._print_post_details(processed_post)
                
                # Respect Reddit's rate limits
                time.sleep(0.5)
            
            self.logger.info(f"Found {len(posts)} new posts from r/{subreddit}")
            return posts
            
        except Exception as e:
            self.logger.error(f"Error fetching posts from r/{subreddit}: {e}")
            return []

    def _print_post_details(self, post_data: Dict[str, Any]):
        """Print detailed information about a post"""
        print("\n" + "="*80)
        print(f"Title: {post_data['title']}")
        print(f"Subreddit: r/{post_data['subreddit']}")
        print(f"URL: {post_data['url']}")
        if 'score' in post_data:
            print(f"Score: {post_data['score']}")
        if 'author' in post_data:
            print(f"Author: u/{post_data['author']}")
        if 'num_comments' in post_data:
            print(f"Comments: {post_data['num_comments']}")
        print(f"Timestamp: {post_data['timestamp']}")
        print("\nContent:")
        print("-"*40)
        print(post_data['content'])
        print("="*80 + "\n")

    def run_continuously(
        self,
        subreddits: List[str],
        check_interval: int = 300  # 5 minutes
    ):
        """
        Continuously monitor subreddits for new posts
        
        Args:
            subreddits: List of subreddit names to monitor
            check_interval: Time between checks in seconds
        """
        self.logger.info(f"Starting continuous monitoring of subreddits: {', '.join(subreddits)}")
        
        while True:
            try:
                for subreddit in subreddits:
                    self.get_posts_from_subreddit(subreddit)
                
                self.logger.info(f"Waiting {check_interval} seconds before next check...")
                time.sleep(check_interval)
                
            except KeyboardInterrupt:
                self.logger.info("Stopping continuous monitoring...")
                break
            except Exception as e:
                self.logger.error(f"Error during continuous monitoring: {e}")
                time.sleep(60)  # Wait a minute before retrying on error

def run_scraper(config_path: str):
    # Initialize the scraper
    scraper = RedditScraper(config_path)
    
    config = scraper.config
    # Run the continuous scraper
    try:
        scraper.run_continuously(
            subreddits=config['reddit']['subreddits'],
            check_interval=config['scraping']['check_interval']  # Check every 5 minutes
        )
    except KeyboardInterrupt:
        logging.info("Scraper stopped by user")
    except Exception as e:
        logging.error(f"Error running scraper: {e}")

if __name__ == "__main__":
    run_scraper('reddit_config.json')