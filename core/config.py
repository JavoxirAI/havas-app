import os
from pathlib import Path

import environ

BASE_DIR = Path(__file__).resolve().parent.parent

# Initialize environment manager
env = environ.Env()

# Try to find .env file in multiple possible locations
env_path = os.path.join(BASE_DIR, '.env')
if not os.path.exists(env_path):
    env_path = os.path.join(BASE_DIR.parent, '.env')


# Read the .env file from the found location
if os.path.exists(env_path):
    environ.Env.read_env(env_path)
else:
    print("⚠️  Warning: .env file not found!")



# DJANGO CORE SETTINGS
SECRET_KEY = env('SECRET_KEY', default='unsafe-secret-key')
DEBUG = env.bool('DEBUG', default=False)
ALLOWED_HOSTS = env.list('ALLOWED_HOSTS', default=['localhost', '127.0.0.1'])

MEDIA_ROOT = env('MEDIA_ROOT', default='/vol/web/media')
STATIC_ROOT = env('STATIC_ROOT', default='/vol/web/static')

# DATABASE SETTINGS
DB_NAME = env('DB_NAME')
DB_USER = env('DB_USER')
DB_PASS = env('DB_PASS')
DB_HOST = env('DB_HOST')
DB_PORT = env('DB_PORT')

# telegram bot
TELEGRAM_BOT_TOKEN = env('TELEGRAM_BOT_TOKEN', default='7701058454:AAGvUTJ_WlkyAxVlrncYU1GZZ6jUZ8Cjebo')
TELEGRAM_CHANNEL_ID = env('TELEGRAM_CHANNEL_ID', default='id')


