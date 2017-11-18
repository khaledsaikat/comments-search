#!/usr/bin/env python3
from flask import Flask
from flask import render_template
from flask import request

from questions import Questions

app = Flask(__name__)


@app.route("/")
def index():
    query = request.args.get("q", "what is parabola")
    query_result = Questions().search(query) if query else {}
    return render_template("index.html", query=query, query_result=query_result)
