"""
Apify Ingestion Service with ERS Calculation
Phase 5, Day 4-5: ERS Logic Optimization + Winner Filter
"""
import time
from typing import Dict, List, Optional
from apify_client import ApifyClient


class ApifyIngestionService:
    """Service for scraping social media posts with ERS calculation"""
    
    # Platform-specific actor IDs (verified working)
    ACTOR_IDS = {
        "instagram": "apify/instagram-hashtag-scraper",
        "linkedin": "apify/linkedin-posts-scraper", 
        "twitter": "apify/twitter-scraper"
    }
    
    def __init__(self, apify_client: ApifyClient, collection, embedder):
        """
        Initialize service
        
        Args:
            apify_client: Apify API client
            collection: ChromaDB collection for storage
            embedder: Embedding function for vectorization
        """
        self.client = apify_client
        self.collection = collection
        self.embedder = embedder
        
    def calculate_ers(self, likes: int, comments: int, shares: int) -> float:
        """
        Calculate Engagement Rate Score (ERS)
        
        Formula: (shares * 0.8) + (comments * 0.5) + (likes * 0.2)
        
        Args:
            likes: Number of likes
            comments: Number of comments
            shares: Number of shares
            
        Returns:
            ERS score as float
        """
        return (shares * 0.8) + (comments * 0.5) + (likes * 0.2)
    
    def filter_top_performers(
        self, 
        posts: List[Dict], 
        percentile: float = 0.2
    ) -> Dict:
        """
        Filter top performing posts by ERS percentile
        
        Args:
            posts: List of posts with ERS scores
            percentile: Top percentile to keep (default 0.2 = top 20%)
            
        Returns:
            Dict with filtered posts and statistics
        """
        if not posts:
            return {
                "winners": [],
                "total_posts": 0,
                "winner_count": 0,
                "cutoff_ers": 0,
                "percentile": percentile
            }
        
        # Sort posts by ERS descending
        sorted_posts = sorted(posts, key=lambda x: x.get("ers", 0), reverse=True)
        
        # Calculate cutoff index (top percentile)
        cutoff_index = max(1, int(len(sorted_posts) * percentile))
        
        # Get top performers
        winners = sorted_posts[:cutoff_index]
        
        # Calculate cutoff ERS (minimum ERS to be a winner)
        cutoff_ers = winners[-1].get("ers", 0) if winners else 0
        
        # Add winner flag to posts
        for post in winners:
            post["is_winner"] = True
            post["percentile_rank"] = (sorted_posts.index(post) + 1) / len(sorted_posts)
        
        # Calculate statistics
        winner_ers_scores = [p.get("ers", 0) for p in winners]
        all_ers_scores = [p.get("ers", 0) for p in sorted_posts]
        
        stats = {
            "winners": winners,
            "total_posts": len(posts),
            "winner_count": len(winners),
            "cutoff_ers": cutoff_ers,
            "percentile": percentile,
            "winner_avg_ers": sum(winner_ers_scores) / len(winner_ers_scores) if winner_ers_scores else 0,
            "overall_avg_ers": sum(all_ers_scores) / len(all_ers_scores) if all_ers_scores else 0,
            "improvement_ratio": (sum(winner_ers_scores) / len(winner_ers_scores)) / (sum(all_ers_scores) / len(all_ers_scores)) if all_ers_scores and winner_ers_scores else 1.0
        }
        
        return stats
    
    def scrape_and_score(
        self, 
        target: str, 
        platform: str, 
        count: int = 20,
        filter_winners: bool = False,
        winner_percentile: float = 0.2
    ) -> Dict:
        """
        Scrape posts from a social media account and calculate ERS
        
        Args:
            target: Username/handle to scrape
            platform: Platform name (instagram, linkedin, twitter, facebook)
            count: Number of posts to scrape (max 100)
            filter_winners: Whether to filter top performers only
            winner_percentile: Top percentile to keep if filtering (default 0.2 = top 20%)
            
        Returns:
            Dict with success status, posts, and statistics
        """
        platform = platform.lower()
        
        # Validate platform
        if platform not in self.ACTOR_IDS:
            return {
                "success": False,
                "error": f"Unsupported platform: {platform}",
                "supported_platforms": list(self.ACTOR_IDS.keys())
            }
        
        actor_id = self.ACTOR_IDS[platform]
        
        # Prepare input based on platform
        run_input = self._prepare_input(target, platform, count)
        
        try:
            # Run actor with retry logic
            posts = self._run_with_retry(actor_id, run_input)
            
            if not posts:
                return {
                    "success": False,
                    "error": "No posts retrieved",
                    "message": f"Could not scrape posts from {target}"
                }
            
            # Calculate ERS for each post
            scored_posts = []
            for post in posts[:count]:
                # Extract engagement metrics based on platform
                if platform == "instagram":
                    likes = post.get("likesCount", 0)
                    comments = post.get("commentsCount", 0)
                    shares = 0  # Instagram doesn't provide shares
                elif platform == "linkedin":
                    likes = post.get("numLikes", 0) or post.get("reactionCount", 0)
                    comments = post.get("numComments", 0) or post.get("commentCount", 0)
                    shares = post.get("numShares", 0) or post.get("shareCount", 0)
                elif platform == "twitter":
                    likes = post.get("likeCount", 0) or post.get("favorite_count", 0)
                    comments = post.get("replyCount", 0)
                    shares = post.get("retweetCount", 0) or post.get("retweet_count", 0)
                else:
                    likes = comments = shares = 0
                
                ers = self.calculate_ers(likes, comments, shares)
                
                # Add engagement data to post
                post["likesCount"] = likes
                post["commentsCount"] = comments
                post["sharesCount"] = shares
                post["ers"] = ers
                scored_posts.append(post)
            
            # Store in ChromaDB
            self._store_posts(scored_posts, target, platform)
            
            # Apply winner filter if requested
            if filter_winners:
                filter_result = self.filter_top_performers(scored_posts, winner_percentile)
                
                return {
                    "success": True,
                    "posts": filter_result["winners"],
                    "all_posts_count": len(scored_posts),
                    "winner_count": filter_result["winner_count"],
                    "cutoff_ers": filter_result["cutoff_ers"],
                    "stats": {
                        "total_posts": filter_result["total_posts"],
                        "winner_count": filter_result["winner_count"],
                        "cutoff_ers": filter_result["cutoff_ers"],
                        "percentile": filter_result["percentile"],
                        "winner_avg_ers": filter_result["winner_avg_ers"],
                        "overall_avg_ers": filter_result["overall_avg_ers"],
                        "improvement_ratio": filter_result["improvement_ratio"]
                    },
                    "platform": platform,
                    "target": target
                }
            
            # Calculate statistics
            stats = self._calculate_stats(scored_posts)
            
            return {
                "success": True,
                "posts": scored_posts,
                "stats": stats,
                "platform": platform,
                "target": target
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "message": f"Failed to scrape {target} on {platform}"
            }
    
    def _prepare_input(self, target: str, platform: str, count: int) -> Dict:
        """Prepare actor input based on platform"""
        
        if platform == "instagram":
            # Instagram hashtag scraper - convert username to hashtag search
            return {
                "hashtags": [target],
                "resultsLimit": count
            }
        elif platform == "linkedin":
            # LinkedIn posts scraper - search by keywords
            return {
                "searchUrl": f"https://www.linkedin.com/search/results/content/?keywords={target}",
                "maxPosts": count
            }
        elif platform == "twitter":
            # Twitter scraper - search by username or keywords
            return {
                "searchTerms": [target],
                "maxTweets": count
            }
        
        return {}
    
    def _run_with_retry(
        self, 
        actor_id: str, 
        run_input: Dict, 
        max_retries: int = 3
    ) -> List[Dict]:
        """
        Run actor with exponential backoff retry logic
        
        Args:
            actor_id: Apify actor ID
            run_input: Input parameters for actor
            max_retries: Maximum number of retry attempts
            
        Returns:
            List of scraped posts
        """
        for attempt in range(max_retries):
            try:
                # Run actor
                run = self.client.actor(actor_id).call(run_input=run_input)
                
                # Get results
                items = []
                for item in self.client.dataset(run["defaultDatasetId"]).iterate_items():
                    items.append(item)
                
                # Rate limiting: wait 2 seconds between requests
                time.sleep(2)
                
                return items
                
            except Exception as e:
                if attempt < max_retries - 1:
                    # Exponential backoff: 2^attempt seconds
                    wait_time = 2 ** attempt
                    print(f"Retry {attempt + 1}/{max_retries} after {wait_time}s: {str(e)}")
                    time.sleep(wait_time)
                else:
                    raise e
        
        return []
    
    def _store_posts(self, posts: List[Dict], target: str, platform: str):
        """Store posts in ChromaDB with metadata"""
        
        documents = []
        metadatas = []
        ids = []
        
        for i, post in enumerate(posts):
            # Extract text content based on platform
            if platform == "instagram":
                text = post.get("caption", "")
            elif platform == "linkedin":
                text = post.get("text", "") or post.get("commentary", "")
            elif platform == "twitter":
                text = post.get("text", "") or post.get("full_text", "")
            else:
                text = post.get("text", "") or post.get("caption", "") or post.get("content", "")
            
            if not text or len(text) < 10:
                continue
            
            # Create metadata
            metadata = {
                "source": platform,
                "target": target,
                "ers": post.get("ers", 0),
                "likes": post.get("likesCount", 0),
                "comments": post.get("commentsCount", 0),
                "shares": post.get("sharesCount", 0),
                "url": post.get("url", "") or post.get("postUrl", ""),
                "timestamp": post.get("timestamp", "") or post.get("createdAt", ""),
                "is_winner": post.get("is_winner", False),
                "percentile_rank": post.get("percentile_rank", 1.0)
            }
            
            documents.append(text)
            metadatas.append(metadata)
            ids.append(f"{platform}_{target}_{i}_{int(time.time())}")
        
        # Add to ChromaDB
        if documents:
            self.collection.add(
                documents=documents,
                metadatas=metadatas,
                ids=ids
            )
    
    def _calculate_stats(self, posts: List[Dict]) -> Dict:
        """Calculate engagement statistics"""
        
        if not posts:
            return {}
        
        ers_scores = [p.get("ers", 0) for p in posts]
        likes = [p.get("likesCount", 0) for p in posts]
        comments = [p.get("commentsCount", 0) for p in posts]
        shares = [p.get("sharesCount", 0) for p in posts]
        
        return {
            "total_posts": len(posts),
            "avg_ers": sum(ers_scores) / len(ers_scores),
            "max_ers": max(ers_scores),
            "min_ers": min(ers_scores),
            "avg_likes": sum(likes) / len(likes),
            "avg_comments": sum(comments) / len(comments),
            "avg_shares": sum(shares) / len(shares),
            "total_engagement": sum(likes) + sum(comments) + sum(shares)
        }
