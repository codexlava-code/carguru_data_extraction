from app.config.config import settings
from routes import app  # This is your WSGI app
from wsgiref.simple_server import make_server

if __name__ == "__main__":
    mode = getattr(settings, 'HOST_ENV', 'development')
    if mode == "production":
        print("Production mode: use gunicorn or waitress!")
    else:
        print("Dev server at: http://localhost:8000")
        make_server('', 8000, app).serve_forever()