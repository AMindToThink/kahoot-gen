import requests
from typing import List
import json
import time

endpointUrl = 'https://query.wikidata.org/sparql'
version = '0.1.0'
created = '2023-02-22'
user_agent_header = 'VanderSearchBot/' + version + ' (https://github.com/HeardLibrary/linked-data/tree/master/vanderbot; mailto:steve.baskauf@vanderbilt.edu)'
request_header_dictionary = {
	'Accept' : 'application/json',
	'User-Agent': user_agent_header
}
search_session = requests.Session()
search_session.headers.update(request_header_dictionary)

class Disambiguate():
    def __init__(self):
        return

    #This section was 
    def search_cirrus(self, search_string: str, http: requests.Session, api_endpoint='https://www.wikidata.org/w/api.php') -> List[dict]:

        request_string = '''{
            "action": "query",
            "format": "json",
            "list": "search",
            "formatversion": "2",
            "srsearch": "''' + search_string + '''"
        }'''

        response = http.get(api_endpoint, params=json.loads(request_string))
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
            response = http.get(api_endpoint, params=json.loads(request_string))
            data = response.json()
            #print(json.dumps(data, indent=2))

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
        i = 1
        print("- Multiple Items came up when you searched '", input_question, ", Did you mean:")
        hits = self.search_cirrus(input_question, search_session)
        # print(json.dumps(hits, indent=2))
        for entry in hits:
            multiple_question[i] = [entry.get("description"), entry.get("qid")]
            print( "-", i,  entry.get("description"))
            i = i + 1
        # Taking user input and converting it to an integer
        time.sleep(0.2)
        user_input = int(input("Enter the corresponding number you mean: "))
        print('The user input is:', user_input )
        answer = multiple_question.get(user_input)
        print("The selected answer:", answer[0], "and the Qid:", answer[1])
        print()
        return answer
if __name__ == "__main__":
    disambiguate = Disambiguate()
    disambiguate.getCollectAnswerQid('Geese')