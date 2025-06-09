import json
import logging
from dotenv import load_dotenv

from wsgiref.simple_server import make_server

from app.config.config import settings
from app.src.carguru_dealership.dealership_scraper import DealershipScraper
from app.src.carguru_vehicle.vehicle_scraper import VehicleScraper
from app.utils.utils import Utils

# Load environment variables from .env file
load_dotenv()

def setup_logging():
    logging.basicConfig(
        filename="app/logs/app.log",
        encoding="utf-8",
        level=logging.INFO,
        format="%(asctime)s - %(levelname)s - %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S"
    )
setup_logging()


import json
import re


class MyFramework:
    def __init__(self):
        self.routes = []
        self.middlewares = []

    def route(self, path, methods=['GET']):
        # Path can have parameters e.g. /scrape/<task>
        def decorator(func):
            pattern = re.compile('^' + re.sub(r'<(\w+)>', r'(?P<\1>[^/]+)', path) + '$')
            self.routes.append({'pattern': pattern, 'methods': methods, 'func': func, 'path': path})
            return func

        return decorator

    def add_middleware(self, middleware_func):
        self.middlewares.append(middleware_func)

    def __call__(self, environ, start_response):
        path = environ.get('PATH_INFO', '/')
        method = environ.get('REQUEST_METHOD', 'GET')
        body = b''
        if method == 'POST':
            content_length = int(environ.get('CONTENT_LENGTH', 0) or 0)
            if content_length > 0:
                body = environ['wsgi.input'].read(content_length)
        try:
            request_data = json.loads(body.decode()) if body else {}
        except Exception:
            request_data = {}

        # Middleware before request
        for mw in self.middlewares:
            mw(path, method, request_data)

        for route in self.routes:
            match = route['pattern'].match(path)
            if match and method in route['methods']:
                try:
                    kwargs = match.groupdict()
                    result = route['func'](request_data, **kwargs)
                    response = json.dumps(result).encode()
                    start_response('200 OK', [('Content-Type', 'application/json')])
                except Exception as e:
                    response = json.dumps({"error": str(e)}).encode()
                    start_response('500 Internal Server Error', [('Content-Type', 'application/json')])
                return [response]

        if path == '/docs':
            return [self._auto_docs(start_response)]

        start_response('404 Not Found', [('Content-Type', 'application/json')])
        return [b'{"error":"not found"}']

    def _auto_docs(self, start_response):
        routes = [
            {
                "path": r['path'],
                "methods": r['methods'],
                "function": r['func'].__name__,
                "doc": r['func'].__doc__
            }
            for r in self.routes
        ]
        start_response('200 OK', [('Content-Type', 'application/json')])
        return json.dumps({"routes": routes}, indent=2).encode()





# class MyFramework:
#     def __init__(self):
#         self.routes = {}
#         self.middlewares = []
#
#     def route(self, path, methods=['GET']):
#         def decorator(func):
#             self.routes[(path, tuple(methods))] = func
#             return func
#
#         return decorator
#
#     def __call__(self, environ, start_response):
#         path = environ.get('PATH_INFO', '/')
#         method = environ.get('REQUEST_METHOD', 'GET')
#         for (route_path, route_methods), func in self.routes.items():
#             if route_path == path and method in route_methods:
#                 # Parse request body if POST
#                 content_length = int(environ.get('CONTENT_LENGTH', 0) or 0)
#                 body = environ['wsgi.input'].read(content_length) if content_length > 0 else b''
#                 try:
#                     request_data = json.loads(body.decode()) if body else {}
#                 except Exception:
#                     request_data = {}
#                 result = func(request_data)
#                 response = json.dumps(result).encode()
#                 start_response('200 OK', [('Content-Type', 'application/json')])
#                 return [response]
#         start_response('404 Not Found', [('Content-Type', 'application/json')])
#         return [b'{"error":"not found"}']




