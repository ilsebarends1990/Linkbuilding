"""
Serverless function handler for Vercel
"""
from http.server import BaseHTTPRequestHandler
import sys
import os

# Add parent directory to path so we can import from there
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import the FastAPI app
from index import app

# Import ASGI handler for serverless
from mangum import Mangum

# Create handler for serverless function
handler = Mangum(app)

# Function to handle all requests
def handler(event, context):
    return Mangum(app)(event, context)
