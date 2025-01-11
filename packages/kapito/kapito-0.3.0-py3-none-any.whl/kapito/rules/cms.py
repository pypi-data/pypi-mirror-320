cms = {
     "wordpress": {
        "cookies": ["wordpress_test_cookie", "wp-settings"],
        "headers": ["X-Pingback"],
        "dom": ["[src*='wp-content']", "[src*='wp-includes']"],
    },
    "joomla": {
        "cookies": ["joomla_remember_me"],
        "headers": ["X-Content-Encoded-By"],
        "dom": ["[src*='joomla']"],
    },
    "drupal": {
        "cookies": ["SESS", "Drupal.visitor"],
        "headers": ["X-Generator", "X-Drupal-Cache"],
        "dom": ["[src*='sites/all/themes']", "[src*='sites/default/files']"],
    },
    "shopify": {
        "cookies": ["_shopify_y", "_shopify_s"],
        "headers": ["X-ShopId", "X-Shopify-Stage"],
        "dom": ["[src*='cdn.shopify.com']"],
    },
    "magento": {
        "cookies": ["frontend", "adminhtml"],
        "headers": ["X-Magento-Vary"],
        "dom": ["[src*='skin/frontend']", "[src*='media/catalog']"],
    },
    "wix": {
        "cookies": ["_wixAB3", "XSRF-TOKEN"],
        "headers": ["X-Wix-Request-Id"],
        "dom": ["[src*='wixstatic.com']", "[src*='/wix/']"],
    },
    "prestashop": {
        "cookies": ["PrestaShop-*"],
        "headers": ["X-Powered-By: PrestaShop"],
        "dom": ["[src*='/themes/prestashop']", "[href*='/modules/prestashop']"],
    },
    "ghost": {
        "cookies": [],
        "headers": ["Ghost-Version"],
        "dom": ["[src*='/ghost/assets']", "[href*='/ghost']"],
    },
    "typo3": {
        "cookies": ["be_typo_user"],
        "headers": ["X-TYPO3"],
        "dom": ["[src*='typo3conf']", "[href*='typo3']"],
    },
    "woocommerce": {
    "cookies": ["woocommerce_items_in_cart", "woocommerce_cart_hash", "wp_woocommerce_session"],
    "headers": [],
    "dom": ["[src*='woocommerce']", "[class*='woocommerce']"],
},
}
