captchas = {
  "turnstile": {
    "dom": ["[src*='cloudflare.com/turnstile/']", "[class*='cf-turnstile']"]
  },
  "hcaptcha": {
    "dom": ["[src*='hcaptcha.com/captcha/']", "[class*='h-captcha']", "[data-hcaptcha-response]"]
  },
  "recaptcha": {
    "dom": [
      "[src*='google.com/recaptcha/api.js']",
      "[src*='recaptcha.net/recaptcha/api.js']",
      "[class*='g-recaptcha']",
      "[data-sitekey^='6L']"
    ]
  },
  "funcaptcha": {
    "dom": ["[src*='funcaptcha.com/fc/api/']", "[src*='arkoselabs.com/fc/api/']", "[data-pkey]"]
  },
  "geetest": {
    "dom": ["[src*='geetest.com/gt.js']",
            "[class*='geetest']",
            "[src*='api.geetest.com']"]
  },
  "keycaptcha": {
    "dom": ["[src*='keycaptcha.com/keycaptcha/']", "[id*='KeyCAPTCHA']"]
  },
  "capy": {
    "dom": ["[src*='api.capy.me/']", "[class*='capy-captcha']"]
  },
  "arkoselabs": {
    "dom": ["[src*='arkoselabs.com/fc/api/']", "[data-callback='arkoseLabsCallback']"]
  },
  "visualcaptcha": {
    "dom": ["[class*='visualCaptcha']", "[id*='visualCaptcha']"]
  },
  "botdetect": {
    "dom": ["[src*='botdetect.com/captcha-lib/']", "[class*='BDC_']"]
  },
  "yandex": {
    "dom": [
      "[src*='captcha-api.yandex.ru/']",
      "[src*='smartcaptcha.yandexcloud.net/']",
      "[class*='smart-captcha']"
    ]
  },
  "amazon": {
    "dom": [
      "[src*='opfcaptcha-prod.s3.amazonaws.com/']",
      "[src*='amazon.com/captcha/']",
      "[class*='amzn-captcha']"
    ]
  },
  "mtcaptcha": {
    "dom": ["[src*='mtcaptcha.com/']", "[class*='mtcap']"]
  },
  "friendlycaptcha": {
    "dom": ["[src*='friendlycaptcha.com/']", "[class*='frc-captcha']"]
  },
  "secureimage": {
    "dom": ["[src*='secureimage.secureserver.net/']"]
  },
  "perimeterx": {
    "dom": ["[src*='perimeterx.net/']", "[class*='px-captcha']"]
  },
  "kasada": {
    "dom": ["[src*='kasada.io/']"]
  },
  "datadome": {
    "dom": ["[src*='datadome.co/']"]
  },
  "solvemedia": {
    "dom": ["[src*='api-secure.solvemedia.com/']", "[class*='adcopy']"]
  }
}
