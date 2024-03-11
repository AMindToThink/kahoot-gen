#ONLY FOR USE WHEN IMPORTING IN OTHER SCRIPTS. THIS IS OUTDATED.
# %%
import requests
from SPARQLWrapper import SPARQLWrapper, JSON
import pandas
import question
import random
import time


# %%
# Predicates
SUBCLASS_OF = "P279"
PART_OF = "P361"
INSTANCE_OF = "P31"

predicates = [SUBCLASS_OF, PART_OF, INSTANCE_OF]

# %%
wikidata_properties = {
    "named_after": "wdt:P138",
    "occupation": "wdt:P106",
    "has_use": "wdt:P366",
    "studied_in": "wdt:P2579",
    "subclass_of": "wdt:P279",
    "part_of": "wdt:P361",
    "field_of_work": "wdt:P101",
    "main_subject": "wdt:P921",
    "located_in_the_administrative_territorial_entity": "wdt:P131",
    "contains_administrative_territorial_entity": "wdt:P150",
    "practiced by": "wdt:P3095"
}


# %%
# Category Example: Team Sports
# Element Example: Baseball
from disambiguate import Disambiguate


class Generator:
    def __init__(self, sister_predicates):
        self.sparql = SPARQLWrapper("https://query.wikidata.org/sparql")
        self.sister_predicates = sister_predicates
        self.check_answer_is_correct_pattern_num_runs = 0
        self.disambiguater = Disambiguate()
    # SPARQL Helper Methods
    def run_query(self, query):
        '''
        Description:
            Takes in query and requests its output
        
        Arguments:
            query:string
        
        Returns:
            results:JSON
        '''
        # Set the query and the return format (JSON)
        self.sparql.setQuery(query)
        self.sparql.setReturnFormat(JSON)

        # Perform the query and convert the result to a Python dictionary
        results = self.sparql.query().convert()
        return results 
    def find_label_by_ID(self, ID):
        '''
        Description:
            Takes in QID and outputs its label
        
        Arguments:
            ID:string - "QXXXXX"
        
        Returns:
            label:string
        '''
        query = f'''
        SELECT ?itemLabel WHERE {{
            wd:{ID} rdfs:label ?itemLabel.
            FILTER(LANG(?itemLabel) = "en")
        }}
        '''
        results = self.run_query(query)
        return results["results"]["bindings"][0]["itemLabel"]["value"]
    def find_uri_by_label(self, label):
        '''
        Description:
            Takes in label and outputs its URI
        
        Arguments:
            label:string
        
        Returns:
            uri:string - 'http://www.wikidata.org/entity/XXXXXXX'
        '''
        
        # Create SPARQL query to find the URI for a given label
        query = f'''SELECT ?item WHERE {{ 
                    ?item rdfs:label "{label.replace('"', '\"')}"@en.
                    SERVICE wikibase:label {{ bd:serviceParam wikibase:language "[AUTO_LANGUAGE],en". }} 
                }} LIMIT 1'''
        
        try:
            results = self.run_query(query)

            # The first matching URI
            binding = results["results"]["bindings"][0]
            result = binding["item"]["value"]
            return result
        except Exception as e:
            print(f"An error occurred: {e}")
            return None
    def find_ID_by_label(self, label, user_input=False):
        '''
        Description:
            Takes in label and outputs its ID
        
        Arguments:
            label:string
            user_input:bool - True if the label is from the user
        
        Returns:
            id:string - 'QXXXXXX'
        '''
        if user_input:
            id = self.disambiguater.getCollectAnswerQid(label)
        else:
            uri = self.find_uri_by_label(label)
            id = uri.split("/")[-1]
        return id
    def find_ID_by_uri(self, uri):
        '''
        Description:
            Takes in uri and outputs its ID
        
        Arguments:
            uri:string - http://www.wikidata.org/entity/QXXXXX or http://www.wikidata.org/prop/direct/PXXXXX 
        
        Returns:
            id:string - 'Q/PXXXXXX'
        '''
        return uri.split('/')[-1]
    def process_JSON(self, results_JSON, desired_variables):
        '''
        Description:
            Takes in output of a query and returns the desired outputs
        
        Arguments:
            results_JSON:JSON
            desired_variables:List(string) - variables wanted from output 
        
        Returns:
            results:List(ID)
        '''
        results = []
        for c in results_JSON['results']['bindings']:
            r = []
            for variable in desired_variables:
                r.append(self.find_ID_by_uri(c[variable]['value']))
            results.append(r)

        return results
    def random_items(self, items, count):
        '''
        Description:
            Takes in a list of items and outputs a random subset of them
        
        Arguments:
            items:list
            count:int
        
        Returns:
            selected:list() - List of count items
        '''
        
        selected = random.sample(items, count)
        return selected

    def sister_category(self, categoryID, avoided_elementIDs, included_elementIDs=[], n_items=3):
        '''
        Description:
            Takes in category and element IDs and outputs related categories that don't contain the element
        
        Arguments:
            categoryID:string
            avoided_elementIDs:list(string) - elements the category shouldn't cover
            included_elementIDs:list(string) - elements the category should cover - unimplemented
            n_items:int
        
        Returns:
            results:List(ID) - IDs of Sister categories of categoryID
            preds:List(ID) - IDS of predicates corresponding to results
            
        '''
        # Prepare elements
        avoided_element_queries = ""
        for elementID in avoided_elementIDs:
            avoided_element_queries += f'wd:{elementID} ?predicates ?category.\n'
        
        # included_element_queries = ""
        # if len(included_elementIDs) != 0:
        #     # included_element_queries += "VALUES ?includedElements {"
        #     for elementID in included_elementIDs:
        #         included_element_queries += f'wd:{elementID} '
        #     # included_element_queries += "}\n"
        #     # included_element_queries += "?includedElements ?predicates ?category.\n"
            


        # Make query
        desired_variables = ["category", "predicate"]
        query = f'''
                SELECT ?category ?categoryLabel ?predicate WHERE {{
                    SERVICE wikibase:label {{ bd:serviceParam wikibase:language "[AUTO_LANGUAGE],en". }}
                    VALUES ?predicates {{ {self.sister_predicates} }}
                    wd:{categoryID} ?predicates ?superCategory.
                    ?category ?predicates ?superCategory.

                    #VALUES ?includedElements {{ included_element_queries }}
                    #?includedElements ?predicates ?category.

                    FILTER(?category != wd:{categoryID})
                    FILTER NOT EXISTS {{
                        {avoided_element_queries}
                    }}
                
                    ?superCategory rdfs:label ?superCategoryLabel .
                    FILTER(LANG(?superCategoryLabel) = "en")
                    ?category rdfs:label ?categoryLabel .
                    FILTER(LANG(?categoryLabel) = "en")
                    BIND(?predicates AS ?predicate)
  
                }}
                LIMIT {n_items}
                #GROUP BY ?category ?categoryLabel
                #HAVING (COUNT(?includedElements) = {len(included_elementIDs)})
        '''
        
        results = self.run_query(query)
        
        results = self.process_JSON(results, desired_variables)
        return [r[0] for r in results], [r[1] for r in results]
    def sister_element(self, elementID, categoryID, exceptions=[], n_items=100):
        '''
        Description:
            Takes in element's ID and its category's ID and outputs related elements not in said category
        
        Arguments:
            elementID:string - "QXXXXX"
            categoryID:string - "QXXXXX"
            exceptions: list 
            n_items:int
        
        Returns:
            results:List(ID) - IDs of Sister topics of label
        '''
        
        #exeptions = [f'FILTER NOT EXISTS {{?item {exception} .}}\n' for exception in exceptions]
        exception_patterns = []
        for exception in exceptions:
            predicate, object = exception.split()
            pattern = f"""FILTER NOT EXISTS {{
                            ?sisterElement {predicate} ?exceptionCategory .
                            ?exceptionCategory (wdt:P279)* {object} .
                        }}\n"""
            exception_patterns.append(pattern)

        exceptions_string = "".join(exception_patterns)

        # Get Sister Catgeories
        sister_categories, sister_preds = self.sister_category(categoryID, [elementID], n_items=n_items)
        sister_preds = list(set(sister_preds))
        # Note: sister_preds[i] represents the predicate used to find sister_categories[i]
        '''
        Example:
        Some superCategory is a category that categoryID is within based on sister_preds[i]
        sister_categories[i] is in superCategory based on sister_preds[i]

        Thus, to find a sister of elementID (more like cousin), the sister_element must be within sister_categories[i] based on sister_preds[i]

        So, let's say the category is team sports.. Team sports is a SUBCLASS_OF sports.
        Animal sports is a SUBCLASS_OF sports
        Horse racing is a SUBCLASS_OF animal sports

        In that example:
        categoryID = team sports
        superCategory = sports
        sister_category[i] = animal sports
        sister_preds[i] = SUBCLASS_OF
        sister of elementID = horse racing

        Using sister_preds ensures that the sister_elements generated are closer to elementID
        '''

        #SPARQL query to find elements that are similar to the elementID but not in categoryID
        desired_variables = ["sisterElement"]
        query = f'''
        SELECT ?sisterElement ?sisterElementLabel WHERE {{
            VALUES ?predicates {{ {"".join([f'wdt:{p} ' for p in sister_preds])} }}
            VALUES ?sisterCategories {{ {"".join([f"wd:{sister} " for sister in sister_categories])} }}
            
            SERVICE wikibase:label {{ bd:serviceParam wikibase:language "[AUTO_LANGUAGE],en". }}
            ?sisterElement ?predicates ?sisterCategories.
            ?sisterElement rdfs:label ?sisterElementLabel.

            FILTER(LANG(?sisterElementLabel) = "en")
            FILTER(?sisterElement != wd:{elementID})
            {exceptions_string}
            
        }}
        
        LIMIT {n_items}
        '''
        
        results = self.run_query(query)
        results = self.process_JSON(results, desired_variables)

        return [r[0] for r in results]
        
    
    # Printing Methods
    def display_as_table(self, results, n_items):
        '''
        Description:
            Creates a table of the n_items of the queried results
        
        Arguments:
            results:JSON - sister topics
            n_items:int
        
        Returns:
            None
        '''
        df = pandas.DataFrame.from_dict(results["results"]["bindings"][:n_items])
        df = df.applymap(lambda x: x["value"])
        pandas.set_option('display.max_rows', n_items) # n_items doesnt work here
        print(df)
    def print_question(self, question):
        '''
        Description:
            Prints the question
        
        Arguments:
            question:Question
        
        Returns:
            None
        '''
        print(f"Which of the following is a {self.find_label_by_ID(question.relation.predicate)} {self.find_label_by_ID(question.relation.object)}?")
       
        print(question.all_answers)
        for index, answer in enumerate(question.all_answers):
            print(f"{index + 1}. {self.find_label_by_ID(answer)}")
   
    # Element-> Category+Elements Question Methods
    '''
    Which of the following is a subclass of Olympic sport?
    1. savika
    2. *baseball*
    3. memory sport
    4. snowshoe biathlon
    '''
    def get_category_relation(self, label):
        '''
        Description:
            Takes in label and outputs one of its categories in the form of a relation
            Relations are pairs of predicates and objects

        Arguments:
            label:string
        
        Returns:
            Relation object
        '''
        topicID = self.find_ID_by_label(label)
        # Randomly choose a ?predicate ?object pair
        desired_variables = ["predicate", "object"]
        query = f'''
        SELECT ?predicate ?object WHERE {{
            VALUES ?predicate {{ {self.sister_predicates} }}
            
            ?object rdfs:label ?label.
            wd:{topicID} ?predicate ?object.
            SERVICE wikibase:label {{ bd:serviceParam wikibase:language "[AUTO_LANGUAGE],en". }}
        }}
        ORDER BY RAND()
        '''
        results = self.process_JSON(self.run_query(query), desired_variables)
        random_relation = self.random_items(results, count=1)[0]

        return question.Relation(random_relation[0], random_relation[1])
    
    def element_question(self, element_label, num_wrong_answers=3):
        '''
        Description:
           Creates a question with the element as the correct answer
        
        Arguments:
            element_label:string
            num_wrong_answers:int
        
        Returns:
            question:Question
        '''
        elementID = self.find_ID_by_label(element_label, user_input=True)
        
        relation = self.get_category_relation(element_label)
        categoryID = relation.object
        wrong_answers = self.sister_element(elementID, categoryID, [str(relation)])

        selected_answers = self.random_items(wrong_answers, count=num_wrong_answers)
        relation = question.Relation( relation.predicate, relation.object)
        return question.Question(relation, elementID, selected_answers)
    def check_answer_is_correct_pattern_r(self, possible_answer, relation):
        return self.check_answer_is_correct_pattern(possible_answer, "wdt:" + relation.predicate, "wd:" + relation.object)
    def check_answer_is_correct_pattern(self, possible_answer, predicate, object):
        '''
        Description:
            Takes in possible answer and relation and generates a pattern to check if the answer is correct
            
        Arguments:
            possible_answer:string
            relation:Relation
            If variable ?v. If QID wd:QID. I can't append wd to things arbitrarily because I want this to handle variables or QIDs
            Similar for predicates and objects
        Returns:
            string - SPARQL query pattern
        '''
        # I don't like this system. There's probably a better way in SPARQL
        uniqueness_num = self.check_answer_is_correct_pattern_num_runs

        predicate_then_subclassstar = f"""{possible_answer} {predicate} ?checkAnswerIntermediate{uniqueness_num} .
                                            ?checkAnswerIntermediate{uniqueness_num} (wdt:P279)* {object} ."""
        # predicate is occupation. Check if possible_answer has a field of work practiced by object
        
        field_of_work_occupation = f"""#check if predicate is occupation
                                    FILTER({predicate} = {wikidata_properties['occupation']})
                                    {possible_answer} {wikidata_properties['field_of_work']} ?checkAnswerField{uniqueness_num} .
                                    ?checkAnswerField{uniqueness_num} {wikidata_properties["practiced by"]} {object} ."""
        # Append the patterns to a list
        patterns = []
        patterns.append(predicate_then_subclassstar)
        patterns.append(field_of_work_occupation)
        # UNION the patterns together
        # put curly braces around the patterns
        patterns = [f"{{{pattern}}}" for pattern in patterns]
        # join the patterns with a newline and a UNION
        patterns = "\nUNION\n".join(patterns)
        print(patterns)
        self.check_answer_is_correct_pattern_num_runs += 1
        return patterns
    def check_answer_using_pattern(self, possible_answer, relation):
        '''
        Description:
            Takes in possible answer and relation and checks if the answer is correct
        
        Arguments:
            possible_answer:string
            relation:Relation
        
        Returns:
            boolean
        '''
        patterns = self.check_answer_is_correct_pattern_r("wd:" + possible_answer, relation)
        query = f'''
        ASK WHERE {{
            {patterns}
        }}
        '''
        #print(query)
        results = self.run_query(query)
        return results['boolean']
    
    # Element(s) -> Categories Question Methods
    '''
    Which of the following is a category baseball, volleyball, basketball, and cricket all belong to?
    1. sport in ancient Greece
    2. *team sport*
    3. racing sports
    4. sport in Europe
    '''
    def find_category(self, elementIDs, predicateID=SUBCLASS_OF):
        '''
        Description:
            Inputs element IDs and outputs a category ID that they all belong to based on the predicate
        
        Arguments:
            elementIDs:list(string)
            predicateID:string
        
        Returns:
            random_categoryID:string -  random category that elementID belongs to
        '''
        # Prepare elements
        element_queries = "".join([f"wd:{e} " for e in elementIDs]) # wd:QXXXX for every element
        
        # Prepare query
        desired_variables = ["category"]
        query = f'''
        SELECT ?category ?label (COUNT(?elements) as ?elementCount) WHERE {{
            VALUES ?elements {{ {element_queries} }}
            ?elements wdt:{predicateID} ?category.
            ?category rdfs:label ?label.

            SERVICE wikibase:label {{ bd:serviceParam wikibase:language "[AUTO_LANGUAGE],en". }}
            FILTER(LANG(?label) = "en")
        }}
        GROUP BY ?category ?label
        HAVING (COUNT(?elements) = {len(elementIDs)})
        '''
           
        categories = self.process_JSON(self.run_query(query), desired_variables)
        if len(categories) == 0:
            print(query)
            raise Exception("These elements do not have a shared category")
        categories = [c[0] for c in categories]
        random_categoryID = self.random_items(categories, count=1)[0]
        
        return random_categoryID
    def print_category_question(self, element_labels, answers, correct_answer):
        '''
        Description:
            Takes in question features and prompts the user with them
        
        Arguments:
            element_labels:list(string)
            answers:list(string) - List of IDs
            correct_answer:string - ID of answer
        
        Returns:
            None
        '''
        # Prepare Questions
        q = "Which of the following is a category that "
        i=0
        while i < len(element_labels) - 1:
            q += f"{element_labels[i]}, "
            i+=1
        
        if len(element_labels) == 1:
            q += f"{element_labels[i]} belongs to"
        else:
            q += f"and {element_labels[i]} all belong to"
        print(q)

        # Print Answers
        for index, answer in enumerate(answers):
            print(f"{index + 1}. {self.find_label_by_ID(answer)}")
        time.sleep(0.2)

        # Input answer and output result
        user_answer = int(input("What is your answer?")) - 1
        if answers[user_answer] == correct_answer:
            print("You are correct!")
        else:
            print("You are incorrect!")
    def category_question(self, element_labels, num_wrong_answers=3):
        '''
        Description:
            Inputs elements and finds 4 categories, one being the one that contains every element
            Then prints the question
        
        Arguments:
            element_labels:list(string)
            num_wrong_answers:int
        
        Returns:
            None
        '''
        # Get category of the elements
        elementIDs = []
        for element_label in element_labels:
            elementIDs.append(self.find_ID_by_label(element_label, user_input=True))
        categoryID = self.find_category(elementIDs) # Default is SUBCLASS_OF
        
        # Get 3 other sister categories that are similar, but not the correct answer
        results, _ = self.sister_category(categoryID, elementIDs, n_items=num_wrong_answers) 
        answers = results + [categoryID]
        random.shuffle(answers)

        # Return the 3 sisters and the correct category
        self.print_category_question(element_labels, answers, categoryID)
        # return categoryID, results, correct_answer_idx, 
      
    

# %%
# print("What element do you want the correct answer to the question to be?", end=": ")
# element = input()
# print(element)
# print("How many questions do you want?", end=": ")
# num_questions = int(input())
# print(num_questions)

# %%
named_after = "wdt:P138"
occupation = "wdt:P106"
has_use = "wdt:P366"
studied_in = "wdt:P2579"
sensible_sister_predicates = f"wdt:P279 wdt:P361 wdt:P101 wdt:P361 wdt:P921 wdt:P131 wdt:P150 {named_after} {occupation} {has_use} {studied_in}"

generator = Generator(sister_predicates=sensible_sister_predicates)

# %%
def question_answer(question):
    generator.print_question(question)
    time.sleep(0.2)

    answer = int(input("What is your answer?")) - 1
    user_answer = generator.find_label_by_ID(question.all_answers[answer])
    print(f"Your answer was {user_answer}")
    #correct_answer = generator.find_label_by_ID(question.correct_answer)
    # I don't think the below is necessary. When the question is generated, it does so with queries on wikidata. This just does a second round of queries
    # to confirm something that was already confirmed.  
    was_correct = generator.check_answer_using_pattern(question.all_answers[answer], question.relation)
    #print(f"The correct answer was {correct_answer}")
    if was_correct:
        print("You are correct!")
    else:
        print("You are incorrect!")
    

# %%
cat_q = generator.category_question(["baseball", "volleyball"])
# question_answer(cat_q)

# %%
my_question = generator.element_question("Joe Biden", 3)
question_answer(my_question)

# %%

def get_wikidata_item(item_id):
    # Wikidata API endpoint
    url = "https://www.wikidata.org/w/api.php"
    
    # Parameters for the API request
    params = {
        "action": "wbgetentities",  # Action to get data about entities
        "ids": item_id,  # ID of the Wikidata item (e.g., Q64 for Berlin)
        "format": "json",  # Response format
        "props": "labels|descriptions|aliases",  # Properties to retrieve: labels, descriptions, and aliases
        "languages": "en"  # Language filter
    }
    
    # Make the GET request to the Wikidata API
    response = requests.get(url, params=params)
    
    # Check if the request was successful
    if response.status_code == 200:
        # Parse the JSON response
        data = response.json()
        
        # Access the item's data
        item_data = data['entities'][item_id]
        
        # Extract and print the label, description, and aliases
        label = item_data['labels']['en']['value']
        description = item_data['descriptions']['en']['value']
        aliases = [alias['value'] for alias in item_data['aliases']['en']]
        
        print(f"Label: {label}")
        print(f"Description: {description}")
        print(f"Aliases: {', '.join(aliases)}")
    else:
        print("Failed to retrieve data")

# Example usage
get_wikidata_item("Q64")

# %%



