#!/usr/bin/env python3

from flask import Flask

app = Flask(__name__)

@app.route('/')
def hello():
    return {'message': 'Hello World', 'status': 'success'}

@app.route('/test')
def test():
    return {'message': 'Test endpoint working', 'status': 'success'}

if __name__ == '__main__':
    print("Starting test server on port 5002...")
    app.run(debug=True, host='0.0.0.0', port=5002)
