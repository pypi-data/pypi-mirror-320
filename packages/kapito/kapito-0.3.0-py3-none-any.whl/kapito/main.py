import sys
from parsel import Selector
from kapito.rules import wafs, captchas, cms
import httpx
from typing import Set, Tuple, Optional
from functools import lru_cache
import re
from urllib.parse import urljoin
import logging
from kapito.utils import normalize_url
from kapito.logger import get_logger

logger = get_logger(__name__)


class Analyzer:
    """A class for analyzing web pages for various security features and content types.

    Attributes:
        compiled_wafs (dict): Pre-compiled WAF detection rules.
        compiled_cms (dict): Pre-compiled CMS detection rules.
        compiled_captchas (dict): Pre-compiled CAPTCHA detection rules.
    """

    def __init__(self, cache_size: int = 128):
        """Initialize the WebAnalyzer with pre-compiled detection rules.

        Args:
            cache_size (int): Size of the LRU cache for selectors.
        """
        self.wafs = self._load_rules(wafs)
        self.cms = self._load_rules(cms)
        self.captchas = self._load_rules(captchas)
        self.html: str = None
        self.headers: dict = None
        self.cookies: dict = None
        self.url: str = None

    @staticmethod
    def _clean_selector(selector: str) -> str:
        """Clean and normalize a CSS selector.

        Args:
            selector (str): Raw CSS selector string.

        Returns:
            str: Cleaned and normalized selector.
        """
        if not selector or not isinstance(selector, str):
            return ""
        # Remove extra whitespace
        selector = selector.strip()
        # Ensure proper quoting for attribute values
        if "*=" in selector and not any(q in selector for q in ["'", '"']):
            selector = re.sub(r'\[(.*?\*=)(.*?)\]', r'[\1"\2"]', selector)
        return selector

    @staticmethod
    def _load_rules(rules: dict) -> dict:
        """Pre-compile detection rules for faster matching.

        Args:
            rules (dict): Rules dictionary in the format:
                {
                    "rulename": {
                        "cookies": ["cookie1", ...],
                        "headers": ["header1", ...],
                        "dom": ["[attr*='value']", ...]
                    }
                }

        Returns:
            dict: Compiled rules with optimized data structures.
        """
        compiled = {}
        for name, rule in rules.items():
            compiled[name] = {
                'headers': set(rule.get('headers', [])),
                'cookies': set(rule.get('cookies', [])),
                'dom': rule.get('dom', [])
            }
        return compiled

    def _check_headers_and_cookies(
        self,
        rules: dict,
        headers: dict,
        cookies: dict
    ) -> Set[str]:
        """Check headers and cookies against compiled rules.

        Args:
            rules (dict): Compiled rules to check against.
            headers (dict): HTTP headers to analyze.
            cookies (dict): Cookies to analyze.

        Returns:
            Set[str]: Set of matched rule names.
        """
        results = set()
        headers_keys = {k.lower(): v for k, v in headers.items()} if headers else {}
        cookies_keys = {k.lower(): v for k, v in cookies.items()} if cookies else {}

        for name, rule in rules.items():
            if rule['headers'] and headers_keys:
                rule_headers = {h.lower() for h in rule['headers']}
                if rule_headers & headers_keys.keys():
                    results.add(name)
                    continue

            if rule['cookies'] and cookies_keys:
                rule_cookies = {c.lower() for c in rule['cookies']}
                if rule_cookies & cookies_keys.keys():
                    results.add(name)

        return results

    @lru_cache(maxsize=128)
    def _create_selector(self, html: str) -> Optional[Selector]:
        """Create and cache a Parsel selector for HTML content.

        Args:
            html (str): HTML content to create selector for.

        Returns:
            Optional[Selector]: Cached Parsel selector instance or None if creation fails.
        """
        if not html:
            return None
        try:
            return Selector(text=html)
        except Exception as e:
            logger.error(f"Error creating selector: {e}")
            return None

    def _safe_css_select(self, selector: Selector, css_path: str) -> bool:
        """Safely perform a CSS selection operation.

        Args:
            selector (Selector): Parsel selector object.
            css_path (str): CSS selector to use.

        Returns:
            bool: True if selector matches and is valid, False otherwise.
        """
        if not selector or not css_path:
            return False

        try:
            cleaned_selector = self._clean_selector(css_path)
            if not cleaned_selector:
                return False
            return bool(selector.css(cleaned_selector))
        except Exception as e:
            logger.error(f"Error applying CSS selector '{css_path}': {e}")
            return False

    def _detect_by_rules(
        self,
        rules: dict
    ) -> list[str]:
        """Detect entities based on rules.

        Args:
            rules (dict): Rules to check against.
            html (Optional[str]): HTML content to analyze.
            headers (Optional[dict]): HTTP headers to analyze.
            cookies (Optional[dict]): Cookies to analyze.

        Returns:
            List[str]: List of detected entities.
        """
        results = self._check_headers_and_cookies(rules, self.headers or {}, self.cookies or {})

        if self.html:
            selector = self._create_selector(self.html)
            if selector:
                for name, rule in rules.items():
                    if rule['dom'] and any(
                        self._safe_css_select(selector, sel)
                        for sel in rule['dom']
                    ):
                        results.add(name)

        return list(results)

    def detect_wafs(self) -> list[str]:
        """Detect Web Application Firewalls (WAFs) on the page.

        Returns:
            List[str]: List of detected WAF names.
        """
        return self._detect_by_rules(self.wafs)

    def detect_cms(self) -> list[str]:
        """Detect Content Management Systems (CMS) on the page.

        Returns:
            List[str]: List of detected CMS names.
        """
        return self._detect_by_rules(self.cms)

    def detect_captchas(self) -> list[str]:
        """Detect captchas on the page.

        Returns:
            List[str]: List of detected captchas types.
        """
        return self._detect_by_rules(self.captchas)

    def detect_favicon(self, base_url: str = None) -> str:
        """
        Detects favicon URL.

        Args:
            base_url (str, optional): The base URL of the website, used for resolving relative URLs

        Returns:
            str: The favicon URL if found, None otherwise
        """
        selector = self._create_selector(self.html)
        favicon_url = None

        # Common favicon-related rel attributes
        favicon_rels = [
            'icon', 'shortcut icon', 'apple-touch-icon', 'apple-touch-icon-precomposed',
            'mask-icon', 'fluid-icon'
        ]

        # Create an XPath expression to match any of the favicon rels
        rel_pattern = '|'.join(favicon_rels)
        xpath_expr = f'//link[re:test(@rel, "{rel_pattern}", "i")]/@href'

        # Find all matching favicon links
        favicon_links = selector.xpath(xpath_expr, namespaces={"re": "http://exslt.org/regular-expressions"}).getall()

        if favicon_links:
            favicon_url = favicon_links[0]  # Take the first match

        # If no explicit favicon found and base_url provided, try default /favicon.ico
        if not favicon_url and base_url:
            favicon_url = urljoin(base_url, '/favicon.ico')

        # Make URL absolute if base_url is provided
        if favicon_url and base_url:
            favicon_url = urljoin(base_url, favicon_url)

        return favicon_url

    def detect_feeds(self) -> list[dict[str, str]]:
        """Detect RSS/Atom and other feed types.

        This method detects various types of web feeds including:
        - RSS feeds (RSS 1.0, 2.0)
        - Atom feeds
        - JSON feeds
        - Alternative feed formats

        It checks both link tags and a tags that might contain feed links.
        Also detects feeds from common feed patterns in URLs.

        Args:
            html (str): HTML content to analyze.

        Returns:
            list[dict[str, str]]: List of detected feeds with details:
                - 'type': Feed type (RSS, Atom, etc.)
                - 'url': Full URL of the feed
                - 'title': Feed title if available
                - 'format': Feed format if detectable
        """
        feeds = []
        selector = self._create_selector(self.html)
        if not selector:
            return feeds

        try:
            # Known feed content types
            feed_types = {
                "application/rss+xml": "RSS",
                "application/atom+xml": "Atom",
                "application/feed+json": "JSON Feed",
                "application/rss": "RSS",
                "application/atom": "Atom",
                "application/xml": "XML Feed",
                "text/xml": "XML Feed"
            }

            # Common feed URL patterns
            feed_patterns = [
                r'/feed/?$',
                r'/rss/?$',
                r'/atom/?$',
                r'\.rss$',
                r'\.atom$',
                r'/feed\.xml$',
                r'/rss\.xml$',
                r'/atom\.xml$',
                r'/feed/entries/?$',
                r'/feeds/?$',
                r'/blog/feed/?$',
                r'/blog\.atom/?$',
                r'/rdf/?$',
                r'/syndicate/?$',
                r'/xml/feed/?$'
            ]

            # Helper function to normalize URLs
            def normalize_url(url: str, base_url: str) -> str:
                """Normalize relative URLs to absolute URLs.

                Args:
                    url (str): URL to normalize
                    base_url (str): Base URL for relative URLs

                Returns:
                    str: Normalized absolute URL
                """
                if not url:
                    return ""
                url = url.strip()
                if url.startswith('//'):
                    return f'https:{url}'
                if url.startswith('/'):
                    return f"{base_url.rstrip('/')}{url}"
                if not url.startswith(('http://', 'https://')):
                    return f"{base_url.rstrip('/')}/{url.lstrip('/')}"
                return url

            # Get base URL for relative URL resolution
            base_url = ""
            base_tag = selector.css('base::attr(href)').get()
            if base_tag:
                base_url = base_tag
            else:
                # Try to extract from canonical link
                canonical = selector.css('link[rel="canonical"]::attr(href)').get()
                if canonical:
                    base_url = canonical
                else:
                    # Use the first og:url as fallback
                    og_url = selector.css('meta[property="og:url"]::attr(content)').get()
                    if og_url:
                        base_url = og_url

            # 1. Check <link> tags
            for link in selector.css('link[rel="alternate"], link[type*="xml"], link[type*="json"]'):
                try:
                    attrs = link.attrib
                    url = attrs.get('href', '').strip()
                    if not url:
                        continue

                    feed_info = {
                        'url': normalize_url(url, base_url),
                        'title': attrs.get('title', '').strip(),
                        'type': None,
                        'format': None
                    }

                    # Determine feed type from content type
                    content_type = attrs.get('type', '').lower()
                    if content_type in feed_types:
                        feed_info['type'] = feed_types[content_type]
                        feed_info['format'] = content_type

                    # Check URL patterns if type is still unknown
                    if not feed_info['type']:
                        for pattern in feed_patterns:
                            if re.search(pattern, url, re.I):
                                feed_info['type'] = 'RSS/Atom'
                                break

                    if feed_info['type']:
                        feeds.append(feed_info)

                except Exception as e:
                    logger.error(f"Error processing link tag: {e}")
                    continue

            # 2. Check <a> tags with feed-like hrefs
            for link in selector.css('a[href*="feed"], a[href*="rss"], a[href*="atom"], a[href*="xml"]'):
                try:
                    url = link.attrib.get('href', '').strip()
                    if not url:
                        continue

                    # Skip if URL is already found
                    normalized_url = normalize_url(url, base_url)
                    if any(f['url'] == normalized_url for f in feeds):
                        continue

                    feed_info = {
                        'url': normalized_url,
                        'title': link.css('::text').get('').strip(),
                        'type': None,
                        'format': None
                    }

                    # Check URL patterns
                    for pattern in feed_patterns:
                        if re.search(pattern, url, re.I):
                            feed_info['type'] = 'RSS/Atom'
                            break

                    if feed_info['type']:
                        feeds.append(feed_info)

                except Exception as e:
                    logger.error(f"Error processing anchor tag: {e}")
                    continue

            # 3. Check meta tags for feeds
            for meta in selector.css('meta[name*="feed"], meta[property*="feed"]'):
                try:
                    url = meta.attrib.get('content', '').strip()
                    if not url:
                        continue

                    normalized_url = normalize_url(url, base_url)
                    if any(f['url'] == normalized_url for f in feeds):
                        continue

                    feed_info = {
                        'url': normalized_url,
                        'title': meta.attrib.get('title', '').strip(),
                        'type': 'RSS/Atom',
                        'format': None
                    }
                    feeds.append(feed_info)

                except Exception as e:
                    logger.error(f"Error processing meta tag: {e}")
                    continue

            # Remove duplicates while preserving order
            seen_urls = set()
            unique_feeds = []
            for feed in feeds:
                if feed['url'] not in seen_urls:
                    seen_urls.add(feed['url'])
                    unique_feeds.append(feed)

            return unique_feeds

        except Exception as e:
            logger.error(f"Error detecting feeds: {e}")
            return []

    def get_page(self, url: str) -> Tuple[str, dict, dict]:
        """Download and process a webpage asynchronously.

        Args:
            url (str): URL of the webpage to download.

        Returns:
            Tuple[str, dict, dict]: Tuple containing:
                - HTML content (str)
                - Cookie dictionary (dict)
                - Header dictionary (dict)
        """
        client = httpx.Client(follow_redirects=True)
        response = client.get(self.url, timeout=10)
        self.html = response.text
        self.cookies = dict(response.cookies)
        self.headers = dict(response.headers)
        return self.html, self.cookies, self.headers

    def analyze(self, url:str) -> dict:
        """Perform complete analysis of a webpage.

        Returns:
            dict: dictionary containing detection results with keys:
                - 'waf': List of detected WAFs
                - 'cms': List of detected CMSs
                - 'captchas': List of detected CAPTCHAs
                - 'feeds': List of detected feed URLs
                - 'favicon': Detected favicon URL
        """
        try:
            self.url = normalize_url(url)
            self.get_page(self.url)
        except Exception as e:
            logger.error(f"Error fetching page: {e}")
            sys.exit(1)
        wafs = self.detect_wafs()
        cms = self.detect_cms()
        captchas = self.detect_captchas()
        favicon = self.detect_favicon()
        feeds = self.detect_feeds()
        return {
            "waf": wafs,
            "cms": cms,
            "captchas": captchas,
            "feeds": feeds,
            "favicon": favicon
        }
