import re

# ===
# Internal Lottery Implementation:
# ===

class Outcome:
    """
    This represents an outcome from a task.
    """
    
    def __init__(self, name, info):
        self.name = name;
        self.occurrences = 0
        self.probability = 0
        self.value = 0
        self.children = {}
        if info[0] < 1: self.probability = info[0]
        else: self.occurrences = info[0]
        
        if isinstance(info[1], dict):
            for k in info[1]:
                self.children[k] = Outcome(k, info[1][k])
        if isinstance(info[1], int) or isinstance(info[1], float):
            self.value = info[1]
                
    def is_composite(self):
        return len(self.children) > 0
    
    def is_belief(self):
        return self.occurrences == 0
    
    def calculate_pondered_value(self):
        if not self.is_composite():
            if self.is_belief(): return self.value * self.probability
            else: return self.value * self.occurrences
        else:
            has_hard_evidence = False
            comp_value = 0
            occs = 0
            for child in self.children.values():
                if child.is_belief():
                    if not has_hard_evidence:
                        comp_value += child.calculate_pondered_value()
                        occs += child.probability
                else:
                    if not has_hard_evidence:
                        has_hard_evidence = True
                        comp_value = child.calculate_pondered_value()
                        occs = child.occurrences
                    else:
                        comp_value += child.calculate_pondered_value()
                        occs += child.occurrences
            return comp_value / occs
        
    def calculate_worst_case(self):
        if not self.is_composite():
            return self.value
        v = self.children.values()[0].calculate_worst_case()
        for child in self.children.values()[1:]:
            cv = child.calculate_worst_case() 
            if cv < v:
                v = cv
        return v
            
                
class Task:
    """
    This represents a task that an agent can execute.
    """
    
    def __init__(self, name, info):
        self.name = name;
        self.outcomes = {}
        for k in info:
            self.outcomes[k] = Outcome(k, info[k])
        
    def calculate_pondered_value(self):
        has_hard_evidence = False
        pond_value = 0
        occs = 0
        for outcome in self.outcomes.values():
            if outcome.is_belief():
                if not has_hard_evidence:
                    pond_value += outcome.calculate_pondered_value()
                    occs += outcome.probability
            else:
                if not has_hard_evidence:
                    has_hard_evidence = True
                    pond_value = outcome.calculate_pondered_value()
                    occs = outcome.occurrences
                else:
                    pond_value += outcome.calculate_pondered_value()
                    occs += outcome.occurrences
        return pond_value / occs
    
    def calculate_worst_case(self):
        v = list(self.outcomes.values())[0].calculate_worst_case()
        for outcome in list(self.outcomes.values())[1:]:
            cv = outcome.calculate_worst_case() 
            if cv < v:
                v = cv
        return v        
            
class Lottery:
    """
    This represents a lottery of actions and outcomes that may be preformed by an agent.
    """
    
    def __init__(self, info):
        self.tasks = {}
        for k in info:
            self.tasks[k] = Task(k, info[k])
            
    def calculate_pondered_values(self):
        vals = {}
        for k in self.tasks:
            vals[k] = self.tasks[k].calculate_pondered_value()
        return vals
    
    def calculate_worst_cases(self):
        vals = {}
        for k in self.tasks:
            vals[k] = self.tasks[k].calculate_worst_case()
        return vals

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
