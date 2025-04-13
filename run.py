#!/usr/bin/env python3
"""
Run the AI Interview Agent application
"""

from app import app

if __name__ == '__main__':
    print("Starting AI Interview Agent...")
    print("Access the application at http://localhost:5000")
    app.run(debug=True, host='0.0.0.0', port=5000)