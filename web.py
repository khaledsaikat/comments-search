#!/usr/bin/env python3
from flask import Flask
from flask import render_template
from flask import request
from flask import json

from questions import Questions

app = Flask(__name__)


@app.route("/")
def index():
    query = request.args.get("q", " ")
    query_result = Questions().search(query) if query else {}
    return render_template("index.html", query=query, query_result=query_result)


@app.route("/suggestion/<query>")
def suggestion(query):
    data = ['Audi', 'BMW', 'Bugatti', 'Ferrari', 'Ford', 'Lamborghini', 'Mercedes Benz', 'Porsche', 'Rolls-Royce',
            'Volkswagen']
    return json.dumps(data), {'Content-Type': 'application/json', 'Access-Control-Allow-Origin': '*'}
