import os

class Config:
    SECRET_KEY = "supersecretkey"
    SQLALCHEMY_DATABASE_URI = "sqlite:///database.db"
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    MPESA_CONSUMER_KEY = "0x6mfH2Buh4phYmChotKxOmuISKHNsoCPHGaJp9xtJ73kUzw"
    MPESA_CONSUMER_SECRET = "ICGbJnwdbEAJP6Ke6jSMuBDGGLTIkUStcZeDnNlMoOxISsl5w9tOeqAIUgaP3LiD"
    MPESA_SHORTCODE = "174379"
    MPESA_PASSKEY = "bfb279f9aa9bdbcf158e97dd71a467cd2e0c893059b10f78e6b72ada1ed2c919"
    MPESA_CALLBACK_URL = "https://ethel-tillable-debera.ngrok-free.dev/mpesa/callback"



