import random
class Relation():
    def __init__(self, predicate, object):
        self.predicate = predicate
        self.object = object
    def __str__(self):
        return "wdt:" + self.predicate + " wd:" + self.object
    def to_dict(self):
        """Converts the Relation object to a dictionary."""
        return {
            'predicate': self.predicate,
            'object': self.object
        }
class Question():
    def __init__(self, relation, correct_answer, wrong_answers):
        self.relation = relation
        self.correct_answer = correct_answer
        self.wrong_answers = wrong_answers
        self.all_answers = [self.correct_answer] + self.wrong_answers
        random.shuffle(self.all_answers)
        self.correct_index = self.all_answers.index(self.correct_answer)
        
    def __str__(self):
        return self.relation.predicate + " " + self.relation.object + " " + self.correct_answer + " " + str(self.wrong_answers)
    
    def __dict__(self):
        return {
            "relation": self.relation.to_dict(),
            "correct_answer": self.correct_answer,
            "wrong_answers": self.wrong_answers,
            "all_answers": self.all_answers,
            "correct_index": self.correct_index
        }
    

