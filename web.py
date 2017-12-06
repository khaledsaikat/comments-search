#!/usr/bin/env python3
from flask import Flask
from flask import render_template
from flask import request
from flask import json

from questions import Questions

app = Flask(__name__)


@app.route("/")
def index():
    query = request.args.get("q", "my")
    query_result = Questions().search(query) if query else {}
    return render_template("index.html", query=query, query_result=query_result)


@app.route("/suggestion/<query>")
def suggestion(query):
    suggestions = Questions().suggestions(query)
    return json.dumps(suggestions), {'Content-Type': 'application/json', 'Access-Control-Allow-Origin': '*'}


@app.route("/debug/<query>")
def debug(query):
    query_result = Questions().search(query)
    return json.dumps(query_result), {'Content-Type': 'application/json', 'Access-Control-Allow-Origin': '*'}
