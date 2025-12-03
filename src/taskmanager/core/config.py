import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

def get_settings():
    return {
         # Server
        "HOST": os.getnv("HOST", "127.0.0.1"),
        "PORT": int(os.getenv("PORT", 8000)),

        # App Metadata
        "APP_NAME": os.getenv("APP_NAME", "Workout Tracker API"),
        "APP_VERSION": os.getenv("APP_VERSION", "1.0.0"),
        "APP_DESCRIPTION": os.getenv("APP_DESCRIPTION", "Backend for workout tracking"),

        # Environment
        "ENVIRONMENT": os.getenv("ENVIRONMENT", "development"),
        "DEBUG": os.getenv("DEBUG", "false").lower() == "true",

        # CORS
        "FRONTEND_URL": os.getenv("FRONTEND_URL", "http://localhost:3000"),

        # Database
        "DATABASE_URL": os.getenv("DATABASE_URL"),

        # Auth
        "AUTH_SECRET_KEY": os.getenv("AUTH_SECRET_KEY"),
        "AUTH_ALGORITHM": os.getenv("AUTH_ALGORITHM", "HS256"),
    }

# Export settings dictionary
settings = get_settings()