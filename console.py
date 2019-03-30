import re
from lottery import *
from agents import *

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
            elif agent_type == "decide-risk":
                self.agent = SafeAgent(agent_type, lottery)
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