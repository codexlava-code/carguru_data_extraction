from werkzeug.serving import run_simple
from routes import app  # Import your WSGI app

if __name__ == "__main__":
    run_simple(
        'localhost',
        8000,
        app,
        use_reloader=True,   # Reload on code changes
        use_debugger=True    # Optional: shows better tracebacks
    )