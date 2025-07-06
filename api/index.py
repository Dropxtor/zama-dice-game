from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from mangum import Mangum
import os
import sys

# Add the current directory to the Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Import your existing server
from server import app

# Wrap FastAPI app with Mangum for serverless deployment
handler = Mangum(app)

# Export for Vercel
def main(request):
    return handler(request, {})