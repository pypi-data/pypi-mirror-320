cdns = {
    "akamai": {
        "cookies": ["akaalb", "ak_bmsc"],
        "headers": ["X-Akamai-Edge-Cache", "X-Akamai-Session-Info"],
        "dom": [],
        },
    "maxcdn": {
        "cookies": [],
        "headers": ["X-CDN-Forward"],
        "dom": ["[src*='maxcdn']"],
        },
    "cloudfront": {
        "cookies": ["CloudFront-Policy", "CloudFront-Signature"],
        "headers": ["X-Amz-Cf-Id", "X-Amz-Cf-Pop"],
        "dom": [],
        },
    "fastly": {
        "cookies": [],
        "headers": ["X-Fastly-Request-ID", "X-Served-By", "X-Cache", "X-Timer"],
        "dom": [],
    },
    "section.io": {
        "cookies": [],
        "headers": ["X-Section-Request-ID", "X-Section-Cache"],
        "dom": [],
    },
    "verizon": {
        "cookies": [],
        "headers": ["X-Via", "X-EdgeConnect-MidMile-RTT", "X-EdgeConnect-Origin-MEX-Latency"],
        "dom": [],
    },
    "stackpath": {
        "cookies": [],
        "headers": ["X-Powered-By", "X-StackPath-Cache"],
        "dom": [],
    },
    "limelight": {
        "cookies": [],
        "headers": ["X-Li-Ftl-Cache", "X-Li-Request-ID"],
        "dom": [],
    },
}
