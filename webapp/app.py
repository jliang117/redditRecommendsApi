from flask import Flask, jsonify, request, abort, send_from_directory
from flask_cors import CORS

import search

app = Flask(__name__)
CORS(app)

@app.route('/')
def hello():
    return app.send_static_file('../README.md')

@app.route('/search', methods=['POST'])
def search_with_posted_string():
    if not request.json:
        abort(400)
    return search.searchAndExtract(request.json['search'])

if __name__ == '__main__':
    app.run(host='0.0.0.0')
