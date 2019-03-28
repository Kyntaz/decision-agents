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
    """
    Agent that decides rationaly.
    """
    
    def decide(self):
        # Select the task with the highest pondered value.
        task_values = self.lottery.calculate_pondered_values()
        best_task = list(task_values)[0]
        best_value = task_values[best_task]
        for k in list(task_values)[1:]:
            if task_values[k] > best_value:
                best_task = k
                best_value = task_values[k]
        return best_task
    
    def sense(self, line):
        line = re.sub(r"[\s+]", "", line) #trim whitespaces
        match = re.match(r"\((?P<value>-?\d+(?:.\d+)?),(?P<outcome>[a-zA-z]\w*(?:\.[a-zA-Z]\w*)*)\)", line)
        value = eval(match.group("value"))
        outcome_ids = match.group("outcome").split('.')
        self.update_observations(value, outcome_ids[0], outcome_ids[1:])
        
    
    def update_observations(self, value, task_name, outcome_list):
        task = self.lottery.tasks[task_name]
        if not outcome_list[0] in task.outcomes:
            task.outcomes[outcome_list[0]] = Outcome(outcome_list[0], (1, 0))
        outcome = task.outcomes[outcome_list[0]]
        
        for outcome_name in outcome_list[1:]:
            if not outcome_name in outcome.children:
                outcome.children[outcome_name] = Outcome(outcome_name, (1, 0))
            outcome = outcome.children[outcome_name]
        outcome.value = value    

class SafeAgent(Agent):
    pass

# Multi Agent Decision:

class ConditionalAgent(Agent):
    pass

class NashAgent(Agent):
    pass

class MixedAgent(Agent):
    pass

# ===
# Console for interaction:
# ===

class Console:
    """
    A class that handles interaction with the agents
    according to the specification.
    """
    
    def __init__(self):
        self.agent = None
        
    def interaction_loop(self):
        while True:
            command = input()
            
            if command == "exit":
                return
            
            match = re.match(r"(?P<command>^[A-Za-z](?:\w|-)*) (?P<lottery>\(.*\)) (?P<ncalls>\d+)", command)
            agent_type = match.group("command")
            lottery = parse_lottery(match.group("lottery"))
            n_calls = eval(match.group("ncalls"))
            
            if agent_type == "decide-rational":
                self.agent = RationalAgent(agent_type, lottery)
            else:
                raise ValueError("Unkown Agent Type.")
            
            for i in range(n_calls):
                print(self.agent.decide())
                result = input()
                
                if result == "exit":
                    return
                
                self.agent.sense(result)
                

if __name__ == "__main__":
    console = Console()
    console.interaction_loop()
    