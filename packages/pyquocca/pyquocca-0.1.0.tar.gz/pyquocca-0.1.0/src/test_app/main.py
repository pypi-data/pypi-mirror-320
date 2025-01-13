import logging

from flask import Flask

app = Flask(__name__)


@app.route("/")
def index():
    logging.info("Did a thing!")
    return "Hello!"


@app.route("/500")
def error():
    raise Exception("Oops!")
