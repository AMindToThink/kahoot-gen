from flask import Flask
# jsonify is a function that returns a json response
from flask import jsonify
import awsgi
app = Flask(__name__)

@app.route("/help")
@app.route("/")
def welcome():
    return """Welcome to the Question Generator API. 
    /disambiguate/<input_question> takes a word as <input_question> and gives some options with QIDs. 
    /question/for_answer/<QID> takes a QID as <QID> and gives a question with 3 wrong answers. You can also pass in the number of wrong answers and fast_mode as True or False."""

@app.route("/disambiguate/<input_question>")
def disambiguate(input_question:str):
    """Get request that takes disambiguation options
    eg the user passes in "joe biden" and the api returns a json of possible matches
    Use '+' to encode spaces in the url
    eg /disambiguate/joe+biden """
    print("Input question is:", input_question)
    from disambiguate import Disambiguate
    disambiguater = Disambiguate()
    return jsonify(disambiguater.search_cirrus(input_question))

@app.route('/question/for_answer/<QID>', defaults={'num_wrong_answers': 3, 'fast_mode': True})
@app.route('/question/for_answer/<QID>/<int:num_wrong_answers>', defaults={'fast_mode': True})
@app.route('/question/for_answer/<QID>/<int:num_wrong_answers>/<fast_mode>')
def question_for_answer(QID:str, num_wrong_answers:int, fast_mode:bool):
    from question_generator_backend import generator
    print("QID is:", QID)
    print("num_wrong_answers is:", num_wrong_answers)
    print("fast_mode is:", fast_mode)
    question = generator.element_question_from_QID(QID, num_wrong_answers, fast_mode)
    return jsonify({"Question data" : question.__dict__(), "Question string": generator.construct_print_question(question)})
    
# The Lambda handler function
def lambda_handler(event, context):
    print("Received event:", event)
    if 'httpMethod' not in event:
        event['httpMethod'] = event['requestContext']['http']['method']
        event['path'] = event['requestContext']['http']['path']
    return awsgi.response(app, event, context)