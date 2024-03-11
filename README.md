# kahoot-gen
## Description
Creating trivia questions can be a time consuming process. Manually creating multiple choice questions involves choosing a topic, thinking of aspects of that topic, turning those aspects into question/correct answer pairs, and generating false answers to the question. An automated program could use the knowledge graph of Wikidata to automate any of these steps. We intend to create a system that takes a topic from the user and generates questions relevant to the topic.

# How to use:
cd into kahoot-gen.
(Recommended: create a new conda environment)
To get the packages:
pip install -r REQUIREMENTS.txt
Open question-generator.ipynb
Run the cells in order.

The cell containing the following code will ask for user input. Input the number associated with  the option you want to choose.
cat_q = generator.category_question(["baseball", "volleyball"])
It will then ask you a question. Input the number associated with the answer you want to choose.
To get questions for different subjects, input a list of strings into category_question you expect to be related in some way.

The next cell runs element_question. Input a topic, a number of wrong answer, and select fast or slow mode. After disambiguating the topic, it will output a question that has your topic as the correct answer. Answer by inputting the number associated with the answer you want to pick.

## Relation Class
A pair of QIDs. One is the predicate, the other is the object. An answer can satisfy the relation if answer predicate object is in Wikidata.

## Question Class
Has a Relation, a right answer, and a list of wrong answers, all represented with QIDs.

## Generator Class
This class is where the bulk of reasoning occurs. It contains several helper methods and methods specifically related to the questions.
It is initialized using a list of predicates that state how elements can be related to each other (e.g., subclass of, instance of, etc.). Additionally, during initialization, a URL wrapper (SPARQLWrapper) is set so that queries can be sent to wikidata. It also uses a Disambiguate class, which is described later on.

### General Helper Methods
run_query: Takes in a correctly formatted query and requests its output

find_label_by_ID: Takes in QID ("QXXXX") and outputs its label. Does this using a query

find_uri_by_label: Takes in label and outputs its URI ("http://www.wikidata.org/XXXXXXX"). Does this using a query

find_ID_by_label: Takes in label and outputs its ID. If the inputted label is from the user, the Disambiguate class is used so that the user's intentions are held

find_ID_by_uri: Takes in uri and outputs its ID

process_JSON: Outputs of SPARQLWrapper are slightly unclear. This method takes in a query output and only outputs a list of what the caller needs

random_items: Takes in a list of items and outputs a random subset of them




sister_category: Takes in a category and element ID(s) and outputs related categories that don't contain the element(s)

sister_element: Takes in element's ID and its category's ID and outputs related elements not in said category. Arguably cousin elements

### Element Question Generator
Element -> Category+Elements

 Inspired by a friend who made a Kahoot where many of the answers were his name, our “Element Question Generator” takes a topic from user input and makes a question where the input is the correct answer. Give it a String for a topic, a number, and choose fast_mode=True or false. Fast mode takes some shortcuts to return an answer, sacrificing randomness and certainty that the other answers are actually wrong.

### Element Question Answer checking
check_answer_is_correct_pattern
possible answer, predicate, object -> string
Generates a pattern that matches if possible answer predicate object, or they satisfy one of our more complicated ways in which an answer can be right, through reasoning.

check_answer_using_pattern
possible_answer , relation -> boolean
Asks whether the possible answer satisfies the relation using check_answer_is_correct_pattern.

### Category Question Generator
Element(s) -> Categories

This set of methods allows the user to create a question based on the inputted element(s). The question will ask which category answer contains every inputted element. The answers will contain one category that contains all elements and another 3 that don't (could hold 0 to n-1)

find_category: Inputs element ID(s) and outputs a category ID that they all belong to based on the inputted predicate

category_question: Inputs element(s) and finds 4 categories, one being the correct answer that contains every element. Then prints the question

## Disambiguate Class

TO DO

## Future Additions
- Improving sister_category so that better sisters can be found. For example, sister categories could contain 1 to n-1 elements more often
- Improving how categories are chosen. Due to limitations of the wikidata KB, some categories and elements are connected weirdly. Could use longer chains so that grandparents+ of elements are taken into account
- Creating other ways to generate questions. Currently, only multiple choice is used. Could create fill-in-the-blank or true-or-false questions. Also could create other question generators, like a Predicate Question Generator (Predicate -> Category+Elements, AKA, input a predicate and output a random that category, one element that is within that category, and three that are in sister categories)

