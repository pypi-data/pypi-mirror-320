wafs = {
    "datadome": {
        "cookies": ["datadome"],
        "headers": ["X-DataDome", "X-DataDome-CID"],
        "dom": ["[src*='captcha-delivery.com']"],
    },
    "imperva": {
        "cookies": ["incap_ses", "visid_incap", "X-Incap-Sess-Cookie-Hdr"],
        "headers": [],
        "dom": ["[src*='/_Incapsula_Resource']"],
    },
    "cloudflare": {
        "cookies": ["__cfduid"],
        "headers": ["Cf-Cache-Status", "Cf-Ray"],
        "dom": ["script[src*='cloudflare.com/turnstile']"],
    },
    "perimeterx": {
        "cookies": ["_px3", "_pxff_cc", "_pxhd", "_pxvid"],
        "headers": [],
        "dom": [],
    },
    "akamai": {
        "cookies": [],
        "headers": ["X-Akamai-Transformed"],
        "dom": []},
    "f5_big_ip": {
        "cookies": ["BIGipServer"],
        "headers": [],
        "dom": [],
        },
    "sucuri": {
        "cookies": [],
        "headers": ["X-Sucuri-ID"],
        "dom": [],
        },
}
