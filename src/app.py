from flask import Flask
# jsonify is a function that returns a json response
from flask import jsonify
application = Flask(__name__)

from disambiguate import Disambiguate


@application.route("/disambiguate/<input_question>")
def disambiguate(input_question):
    """Get request that takes disambiguation options
    eg the user passes in "joe biden" and the api returns a json of possible matches"""
    print("Input question is:", input_question)
    disambiguater = Disambiguate()
    return jsonify(disambiguater.search_cirrus(input_question))

# @application.route("")