import re
from dependencies import pulp
from lottery import *

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
    """
    Avoids having a negative reward and distributes its effort
    ammong many tasks.
    """
    
    def decide(self):
        # The agent distributes its effort ammong the tasks
        # avoiding the possibility of having a negative
        # reward. This equates to a linear programming
        # problem that will be solved with PuLP, a Linear
        # Programming solver for python.
        
        problem = pulp.LpProblem("DistributeEffort", pulp.LpMaximize)
        
        expected_reward = self.lottery.calculate_pondered_values()
        worst_case = self.lottery.calculate_worst_cases()
        problem_info = {}
        obj = {}
        non_negative = {}
        
        for task in self.lottery.tasks:
            problem_info[task] = (pulp.LpVariable(task, 0, 1), expected_reward[task], worst_case[task])
            obj[problem_info[task][0]] = expected_reward[task]
            non_negative[problem_info[task][0]] = worst_case[task]
            
        non_negative_constraint = pulp.LpAffineExpression(non_negative) >= 0
        total_value_constraint = pulp.lpSum([x[0] for x in problem_info.values()]) == 1
        obj_func = pulp.LpAffineExpression(obj)
        problem += non_negative_constraint
        problem += total_value_constraint
        problem += obj_func
        problem.solve()
        
        sol = "("
        for x in [x[0] for x in problem_info.values()]:
            v = pulp.value(x)
            if v > 0: sol += str(round(v,2)) +  "," + x.name + ";"
        sol = sol[:-1] + ")"
        return sol
    
    def sense(self, line):
        pass # This one doesn't learn, so it does not need to sense.

# Multi Agent Decision:

class ConditionalAgent(Agent):
    pass

class NashAgent(Agent):
    pass

class MixedAgent(Agent):
    pass
