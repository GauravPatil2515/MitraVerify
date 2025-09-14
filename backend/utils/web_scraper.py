"""
MitraVerify Web Scraper
Collects articles from Indian fact-checking and news websites
"""

import requests
import time
import random
import logging
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional
from urllib.parse import urljoin, urlparse
import re
from bs4 import BeautifulSoup
import json
import os
from dataclasses import dataclass
from concurrent.futures import ThreadPoolExecutor, as_completed

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class ScrapedArticle:
    """Data class for scraped article data"""
    url: str
    title: str
    content: str
    published_date: Optional[datetime]
    author: Optional[str]
    tags: List[str]
    summary: Optional[str]

class MitraVerifyScraper:
    """Web scraper for Indian fact-checking and news websites"""

    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'MitraVerify-Bot/1.0 (https://mitraverify.vercel.app)',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
        })

        # Rate limiting
        self.request_delay = 2  # seconds between requests
        self.last_request_time = 0

        # Scraping targets
        self.sources = {
            'altnews': {
                'base_url': 'https://www.altnews.in',
                'article_selector': 'article, .post, .entry',
                'title_selector': 'h1, .entry-title, .post-title',
                'content_selector': '.entry-content, .post-content, article p',
                'date_selector': '.entry-date, .post-date, time',
                'author_selector': '.author, .byline',
            },
            'boom': {
                'base_url': 'https://www.boomlive.in',
                'article_selector': 'article, .article-card',
                'title_selector': 'h1, .article-title',
                'content_selector': '.article-content, .content p',
                'date_selector': '.article-date, time',
                'author_selector': '.author-name',
            },
            'factly': {
                'base_url': 'https://factly.in',
                'article_selector': '.post, article',
                'title_selector': 'h1, .post-title',
                'content_selector': '.post-content, .entry-content p',
                'date_selector': '.post-date, time',
                'author_selector': '.post-author',
            },
            'vishvas': {
                'base_url': 'https://www.vishvasnews.com',
                'article_selector': '.post, article',
                'title_selector': 'h1, .entry-title',
                'content_selector': '.entry-content p, .post-content p',
                'date_selector': '.entry-date, time',
                'author_selector': '.author-name',
            },
            'pib': {
                'base_url': 'https://www.pib.gov.in',
                'article_selector': '.news-article, article',
                'title_selector': 'h1, .article-title',
                'content_selector': '.article-content p, .news-content p',
                'date_selector': '.article-date, time',
                'author_selector': '.author',
            }
        }

    def _rate_limit(self):
        """Implement rate limiting"""
        current_time = time.time()
        time_since_last = current_time - self.last_request_time

        if time_since_last < self.request_delay:
            sleep_time = self.request_delay - time_since_last + random.uniform(0.5, 1.5)
            time.sleep(sleep_time)

        self.last_request_time = time.time()

    def _make_request(self, url: str, max_retries: int = 3) -> Optional[requests.Response]:
        """Make HTTP request with retry logic"""
        for attempt in range(max_retries):
            try:
                self._rate_limit()
                response = self.session.get(url, timeout=30)

                if response.status_code == 200:
                    return response
                elif response.status_code == 429:  # Rate limited
                    wait_time = int(response.headers.get('Retry-After', 60))
                    logger.warning(f"Rate limited, waiting {wait_time} seconds")
                    time.sleep(wait_time)
                    continue
                elif response.status_code >= 400:
                    logger.error(f"HTTP {response.status_code} for {url}")
                    return None

            except requests.exceptions.RequestException as e:
                logger.error(f"Request failed for {url}: {e}")
                if attempt < max_retries - 1:
                    time.sleep(2 ** attempt)  # Exponential backoff
                continue

        return None

    def _extract_article_data(self, soup: BeautifulSoup, source_config: Dict) -> Optional[ScrapedArticle]:
        """Extract article data from BeautifulSoup object"""
        try:
            # Extract title
            title_elem = soup.select_one(source_config['title_selector'])
            title = title_elem.get_text().strip() if title_elem else ""

            if not title:
                return None

            # Extract content
            content_elems = soup.select(source_config['content_selector'])
            content = ' '.join([elem.get_text().strip() for elem in content_elems])

            if not content or len(content) < 100:
                return None

            # Extract date
            date_elem = soup.select_one(source_config['date_selector'])
            published_date = None
            if date_elem:
                date_text = date_elem.get_text().strip()
                # Try to parse various date formats
                try:
                    published_date = datetime.fromisoformat(date_text.replace('Z', '+00:00'))
                except:
                    try:
                        published_date = datetime.strptime(date_text, '%Y-%m-%d')
                    except:
                        published_date = datetime.now()

            # Extract author
            author_elem = soup.select_one(source_config['author_selector'])
            author = author_elem.get_text().strip() if author_elem else None

            # Extract tags (look for common tag selectors)
            tags = []
            tag_selectors = ['.tags a', '.categories a', '.post-tags a', '.article-tags a']
            for selector in tag_selectors:
                tag_elems = soup.select(selector)
                if tag_elems:
                    tags.extend([tag.get_text().strip() for tag in tag_elems])
                    break

            # Generate summary (first 200 characters)
            summary = content[:200] + "..." if len(content) > 200 else content

            return ScrapedArticle(
                url="",  # Will be set by caller
                title=title,
                content=content,
                published_date=published_date,
                author=author,
                tags=tags,
                summary=summary
            )

        except Exception as e:
            logger.error(f"Error extracting article data: {e}")
            return None

    def scrape_article(self, url: str, source_name: str) -> Optional[ScrapedArticle]:
        """Scrape a single article"""
        try:
            logger.info(f"Scraping article: {url}")

            response = self._make_request(url)
            if not response:
                return None

            soup = BeautifulSoup(response.content, 'html.parser')
            source_config = self.sources.get(source_name)

            if not source_config:
                logger.error(f"No configuration found for source: {source_name}")
                return None

            article = self._extract_article_data(soup, source_config)
            if article:
                article.url = url

            return article

        except Exception as e:
            logger.error(f"Error scraping article {url}: {e}")
            return None

    def discover_article_urls(self, source_name: str, max_pages: int = 5) -> List[str]:
        """Discover article URLs from a source's main page and archives"""
        urls = []
        source_config = self.sources.get(source_name)

        if not source_config:
            return urls

        base_url = source_config['base_url']

        # Common URL patterns for article discovery
        url_patterns = [
            base_url,  # Main page
            f"{base_url}/category/fact-check/",
            f"{base_url}/fact-check/",
            f"{base_url}/news/",
            f"{base_url}/articles/",
        ]

        for page_url in url_patterns[:max_pages]:
            try:
                response = self._make_request(page_url)
                if not response:
                    continue

                soup = BeautifulSoup(response.content, 'html.parser')

                # Find article links
                article_links = soup.find_all('a', href=True)

                for link in article_links:
                    href = link['href']

                    # Convert relative URLs to absolute
                    if href.startswith('/'):
                        href = urljoin(base_url, href)
                    elif not href.startswith('http'):
                        continue

                    # Filter for article URLs (avoid navigation, categories, etc.)
                    if self._is_article_url(href, base_url):
                        if href not in urls:
                            urls.append(href)

                # Limit to prevent overwhelming
                if len(urls) >= 50:
                    break

            except Exception as e:
                logger.error(f"Error discovering URLs from {page_url}: {e}")
                continue

        logger.info(f"Discovered {len(urls)} article URLs from {source_name}")
        return urls[:50]  # Limit to 50 URLs per source

    def _is_article_url(self, url: str, base_url: str) -> bool:
        """Determine if a URL likely points to an article"""
        try:
            parsed = urlparse(url)
            path = parsed.path.lower()

            # Skip non-article URLs
            skip_patterns = [
                '/category/', '/tag/', '/author/', '/page/', '/search/',
                '/about/', '/contact/', '/privacy/', '/terms/',
                '/wp-admin/', '/wp-content/', '/wp-includes/',
                '.jpg', '.png', '.gif', '.pdf', '.zip'
            ]

            for pattern in skip_patterns:
                if pattern in path:
                    return False

            # Must be from the same domain
            if parsed.netloc != urlparse(base_url).netloc:
                return False

            # Must have a meaningful path
            if len(path) < 5 or path.count('/') < 1:
                return False

            return True

        except:
            return False

    def scrape_source(self, source_name: str, max_articles: int = 10) -> List[ScrapedArticle]:
        """Scrape articles from a specific source"""
        logger.info(f"Starting scrape of {source_name}")

        # Discover article URLs
        article_urls = self.discover_article_urls(source_name)

        if not article_urls:
            logger.warning(f"No article URLs found for {source_name}")
            return []

        # Scrape articles
        articles = []
        for url in article_urls[:max_articles]:
            article = self.scrape_article(url, source_name)
            if article:
                articles.append(article)
                logger.info(f"Successfully scraped: {article.title[:50]}...")

            # Small delay between articles
            time.sleep(random.uniform(1, 3))

        logger.info(f"Completed scraping {source_name}: {len(articles)} articles")
        return articles

    def scrape_all_sources(self, max_articles_per_source: int = 10) -> Dict[str, List[ScrapedArticle]]:
        """Scrape articles from all configured sources"""
        results = {}

        for source_name in self.sources.keys():
            try:
                articles = self.scrape_source(source_name, max_articles_per_source)
                results[source_name] = articles
                logger.info(f"Scraped {len(articles)} articles from {source_name}")

                # Longer delay between sources
                time.sleep(random.uniform(5, 10))

            except Exception as e:
                logger.error(f"Error scraping {source_name}: {e}")
                results[source_name] = []

        return results

    def save_articles_to_json(self, articles: List[ScrapedArticle], filename: str):
        """Save scraped articles to JSON file"""
        data = []
        for article in articles:
            data.append({
                'url': article.url,
                'title': article.title,
                'content': article.content,
                'published_date': article.published_date.isoformat() if article.published_date else None,
                'author': article.author,
                'tags': article.tags,
                'summary': article.summary,
                'scraped_date': datetime.now().isoformat()
            })

        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)

        logger.info(f"Saved {len(articles)} articles to {filename}")

def main():
    """Main function for testing the scraper"""
    scraper = MitraVerifyScraper()

    # Test single source
    print("Testing scraper with AltNews...")
    articles = scraper.scrape_source('altnews', max_articles=3)

    if articles:
        print(f"Successfully scraped {len(articles)} articles")
        for article in articles[:2]:  # Show first 2
            print(f"- {article.title[:60]}...")
    else:
        print("No articles scraped")

    # Save to file
    if articles:
        scraper.save_articles_to_json(articles, 'scraped_articles_test.json')

if __name__ == '__main__':
    main()