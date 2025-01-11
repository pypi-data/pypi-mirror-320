from urllib.parse import urlparse

def get_base_url(url: str) -> str:
    """
    Extracts the base URL from a given URL.

    Args:
        url (str): The full URL to extract base from

    Returns:
        str: The base URL (scheme + netloc)

    Examples:
        >>> get_base_url('https://example.com/path/page.html?q=123#section')
        'https://example.com'
        >>> get_base_url('http://sub.example.com/path/')
        'http://sub.example.com'
    """
    parsed = urlparse(url)
    return f"{parsed.scheme}://{parsed.netloc}"

from urllib.parse import urlparse, urlunparse, urljoin

def normalize_url(url: str, default_scheme: str = "https") -> str:
    """
    Normalizes a URL by ensuring it has a scheme (e.g., https://) and a valid structure.

    Args:
        url (str): The URL to normalize.
        default_scheme (str): The default scheme to use if none is provided (default is "https").

    Returns:
        str: The normalized URL.

    Examples:
        >>> normalize_url("google.com")
        'https://google.com'
        >>> normalize_url("www.google.com")
        'https://www.google.com'
        >>> normalize_url("http://google.com")
        'http://google.com'
        >>> normalize_url("https://google.com")
        'https://google.com'
        >>> normalize_url("ftp://google.com")
        'ftp://google.com'
    """
    if not url:
        return ""

    # Add a scheme if missing
    parsed = urlparse(url)
    if not parsed.scheme:
        # If the URL starts with "www.", prepend the default scheme
        if url.startswith("www."):
            url = f"{default_scheme}://{url}"
        else:
            # Otherwise, assume it's a domain and prepend the default scheme
            url = f"{default_scheme}://{url}"
        parsed = urlparse(url)

    # Ensure the netloc (domain) is present
    if not parsed.netloc:
        # If the URL is just a path (e.g., "google.com"), treat it as a domain
        if parsed.path and not parsed.path.startswith("/"):
            url = f"{default_scheme}://{parsed.path}"
            parsed = urlparse(url)

    # Reconstruct the URL to ensure it's properly formatted
    normalized_url = urlunparse(
        (
            parsed.scheme,
            parsed.netloc,
            parsed.path,
            parsed.params,
            parsed.query,
            parsed.fragment,
        )
    )

    return str(normalized_url)

