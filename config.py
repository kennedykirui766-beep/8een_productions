import os
from dotenv import load_dotenv
import cloudinary

load_dotenv()

class Config:
    SECRET_KEY = os.getenv("SECRET_KEY")
    SQLALCHEMY_DATABASE_URI = os.getenv("DATABASE_URL")
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_ENGINE_OPTIONS = {
        "pool_pre_ping": True,
        "pool_recycle": 300
    }

    MPESA_CONSUMER_KEY = os.getenv("MPESA_CONSUMER_KEY")
    MPESA_CONSUMER_SECRET = os.getenv("MPESA_CONSUMER_SECRET")
    MPESA_SHORTCODE = os.getenv("MPESA_SHORTCODE")
    MPESA_PASSKEY = os.getenv("MPESA_PASSKEY")
    MPESA_CALLBACK_URL = os.getenv("MPESA_CALLBACK_URL")
    LOGO_URL = "https://res.cloudinary.com/dvctsb0sm/image/upload/v1772306934/file_00000000b2a4722f9b60f61ab86bc14c_ijpfr6.png"
    ABOUT_IMAGE_URL = "https://res.cloudinary.com/dvctsb0sm/image/upload/v1772266168/about.jpg_yicnh1.jpg"
    HERO_IMAGE_URL = "https://res.cloudinary.com/dvctsb0sm/image/upload/v1772703139/hero_section.jpg_fk1jux.jpg"
    SHORT_FILM_URL ="https://res.cloudinary.com/dvctsb0sm/video/upload/v1772710297/5129-183300007_medium_wwue5k.mp4"
    TRACK_URL ="https://res.cloudinary.com/dvctsb0sm/video/upload/v1772710385/36746-412873626_medium_xbjoxb.mp4"
    BRAND_URL ="https://res.cloudinary.com/dvctsb0sm/video/upload/v1772710421/276047_medium_aycbtb.mp4"


cloudinary.config(
    cloud_name=os.environ.get("CLOUDINARY_CLOUD_NAME"),
    api_key=os.environ.get("CLOUDINARY_API_KEY"),
    api_secret=os.environ.get("CLOUDINARY_API_SECRET"),
    secure=True
)