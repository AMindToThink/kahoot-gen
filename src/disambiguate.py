import requests
from typing import List
import json
from SPARQLWrapper import SPARQLWrapper

class Disambiguate():
    def __init__(self):
        return

    def search_cirrus(self, search_string: str, api_endpoint='https://www.wikidata.org/w/api.php') -> List[dict]:

        request_string = '''{
            "action": "query",
            "format": "json",
            "list": "search",
            "formatversion": "2",
            "srsearch": "''' + search_string + '''"
        }'''

        response = requests.get(api_endpoint, params=json.loads(request_string))
        data = response.json()

        hits = data['query']['search']
        # Look up the label for each item
        for index, hit in enumerate(hits):
            # "title" in the search results is the Q ID		
            request_string = '''{
                "action": "wbgetentities",
                "format": "json",
                "ids": "''' + hit['title'] + '''",
                "props": "labels"
            }'''
            response = requests.get(api_endpoint, params=json.loads(request_string))
            data = response.json()

            # Match the Q ID to the label and add the label to the hits list
            try:
                hits[index]['label'] = data['entities'][hit['title']]['labels']['en']['value']
            except:
                hits[index]['label'] = ''

        # Clean up the hits list by removing useless keys and renaming others
        clean_hits = []
        for hit in hits:
            del hit['ns']
            del hit['pageid']
            del hit['size']
            del hit['wordcount']
            del hit['timestamp']
            hit['qid'] = hit['title']
            del hit['title']
            hit['description'] = hit['snippet']
            del hit['snippet']
            clean_hits.append(hit)


        return clean_hits
    
    def getCollectAnswerQid(self, input_question):
        multiple_question = {}
        returned_qid = []
        i = 1
        print("- Multiple Items came up when you searched '", input_question, ", Did you mean:")
        hits = self.search_cirrus(input_question)
        # print(json.dumps(hits, indent=2))
        for entry in hits:
            multiple_question[i] = [entry.get("description"), entry.get("qid")]
            print( "-", i,  entry.get("description"))
            returned_qid.append(entry.get("qid"))
            i = i + 1
        # Taking user input and converting it to an integer
        user_input = int(input("Enter the corresponding number you mean: "))
        print('The user input is:', user_input )
        answer = multiple_question.get(user_input)
        print("The selected answer:", answer[0], "and the Qid:", answer[1])
        return answer[1]
    
    def construct_query(self, returned_qid):
        # for item in returned_qid:
        query = '''
        CONSTRUCT {
        wd:''' + returned_qid + ''' ?p1 ?o.
        ?s ?p2 wd:''' + returned_qid + '''.
        }
        WHERE {
        {wd:''' + returned_qid + ''' ?p1 ?o.}
        UNION
        {?s ?p2 wd:''' + returned_qid + '''.}
        }
        '''
        print(query)
if __name__ == "__main__":
    
    disambiguate = Disambiguate()
    returned_qid = disambiguate.getCollectAnswerQid('politician')
    disambiguate.construct_query(returned_qid)
