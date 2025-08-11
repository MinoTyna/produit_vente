import os

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': os.getenv('DB_NAME', 'aufsarl1_vente'),
        'USER': os.getenv('DB_USER', 'aufsarl1_cpses_aumfwfliib'),
        'PASSWORD': os.getenv('DB_PASSWORD', 'If1ISBxFvLpu6neIP22iRfbwqMS8tG2J'),
        'HOST': os.getenv('DB_HOST', 'localhost'),
        'PORT': os.getenv('DB_PORT', '5432'),
    }
}
