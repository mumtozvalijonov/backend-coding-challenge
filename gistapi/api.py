"""
Exposes a simple HTTP API to search a users Gists via a regular expression.

Github provides the Gist service as a pastebin analog for sharing code and
other develpment artifacts.  See http://gist.github.com for details.  This
module implements a Flask server exposing two endpoints: a simple ping
endpoint to verify the server is up and responding and a search endpoint
providing a search across all public Gists for a given Github account.
"""

import asyncio
from flask import Flask, jsonify
from flask_pydantic import validate


from .filters import GistSearchQuery
from .serializers import GistSearchBody
from .utils import GistMatcher, gists_for_user_generator


app = Flask(__name__)
loop = asyncio.new_event_loop()


@app.route("/ping")
def ping():
    """Provide a static response to a simple GET request."""
    return "pong"


@app.route("/api/v1/search", methods=['POST'])
@validate()
def search(body: GistSearchBody, query: GistSearchQuery):
    """Provides matches for a single pattern across a single users gists.

    Pulls down a list of all gists for a given user and then searches
    each gist for a given regular expression.

    Returns:
        A Flask Response object of type application/json.  The result
        object contains the list of matches along with a 'status' key
        indicating any failure conditions.
    """
    username = body.username
    pattern = body.pattern

    result = {}
    gists_generator = gists_for_user_generator(username)

    matcher = GistMatcher(loop, pattern)
    matches = matcher.get_matching_gists(
        gists_generator, query.limit, query.offset)

    result['status'] = 'success'
    result['username'] = username
    result['pattern'] = pattern
    result['matches'] = matches

    return jsonify(result)
