import os

from flask import Flask, jsonify, request

import search

app = Flask(__name__)

@app.route('/')
def hello():
    return 'Hello world!'

@app.route('/search', methods=['POST'])
def search_with_posted_string():
    if not request.json:
        abort(400)
    return search.searchAndExtract(request.json['search'])

if __name__ == '__main__':
    app.run(host='0.0.0.0')
