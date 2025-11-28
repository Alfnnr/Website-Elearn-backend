import os

# JWT Configuration
SECRET_KEY = os.getenv("SECRET_KEY", "secretjwtkey123")  # Ganti dengan environment variable di production
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 1  # Token akan expired setelah 1 jam tanpa aktivitas

# Database Configuration (jika diperlukan di masa depan)
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./elearn.db")