import re

# Internal Lottery Implementation:

class Outcome:
    """
    This represents an outcome from a task.
    """
    
    def __init__(self, name, info):
        self.name = name;
        self.probability = 0
        self.occurrences = 0
        self.value = 0
        self.children = {}
        if isinstance(info, dict):
            for k in info:
                self.children[k] = Outcome(k, info[k])
        if isinstance(info, tuple):
            if info[0] < 1:
                self.probability = info[0]
                self.value = info[1]
            else:
                self.occurrences = info[0]
                self.value = info[1]
                
class Task:
    """
    This represents a task that an agent can execute.
    """
    
    def __init__(self, name, info):
        self.name = name;
        self.outcomes = {}
        for k in info:
            self.outcomes[k] = Outcome(k, info[k])
            
class Lottery:
    """
    This represents a lottery of actions and outcomes that may be preformed by an agent.
    """
    
    def __init__(self, info):
        self.tasks = {}
        for k in info:
            self.tasks[k] = Task(k, info[k])

def parse_lottery(s):
    # This is just a hack so that I don't have to waste time writting a parser for the lottery
    # language. Please don't judge me.
    
    prepared_s = re.sub(r"[\s+]", "", s)
    prepared_s = "{" + prepared_s[1:-1] + "}"
    prepared_s = re.sub(r"\[", "{", prepared_s)
    prepared_s = re.sub(r"\]", "}", prepared_s)
    prepared_s = re.sub(r"\=", ":", prepared_s)
    prepared_s = re.sub(r"[a-zA-Z]\w*(\|[a-zA-Z]\w*)*", lambda m: "\"" + m.group() + "\"", prepared_s)
    prepared_s = re.sub(r"\d+(\.\d+)?%", lambda m: str(float(m.group()[:-1]) / 100), prepared_s)
    structure = eval(prepared_s)
    return Lottery(structure)