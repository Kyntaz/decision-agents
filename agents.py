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
            for child in self.children.values():
                if child.is_belief():
                    if not has_hard_evidence: comp_value += child.calculate_pondered_value()
                else:
                    if not has_hard_evidence:
                        has_hard_evidence = True
                        comp_value = child.calculate_pondered_value()
                    else:
                        comp_value += child.calculate_pondered_value()
            return comp_value
            
                
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
        for outcome in self.outcomes.values():
            if outcome.is_belief():
                if not has_hard_evidence: pond_value += outcome.calculate_pondered_value()
            else:
                if not has_hard_evidence:
                    has_hard_evidence = True
                    pond_value = outcome.calculate_pondered_value()
                else:
                    pond_value += outcome.calculate_pondered_value()
        return pond_value        
            
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

# ===
# Agents Implementation:
# ===

class Agent:
    """
    A base class for implementing inteligent agents.
    """
    
    def __init__(self, name, lottery):
        self.name = name
        self.lottery = lottery
        
# Single Agent Decision:
        
class RationalAgent(Agent):
    pass

class SafeAgent(Agent):
    pass

# Multi Agent Decision:

class ConditionalAgent(Agent):
    pass

class NashAgent(Agent):
    pass

class MixedAgen(Agent):
    pass

# ===
# Console for interaction:
# ===

class Console:
    pass