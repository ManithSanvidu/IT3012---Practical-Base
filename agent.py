# agent.py
import random
from collections import deque
import heapq

class GreedyGridAgent:
    """A simple agent that tries to move around systematically to clear the grid."""

    def __init__(self):
        self.actions_pool = ['Up', 'Down', 'Left', 'Right']

    def sense_and_act(self, percept: dict) -> str:
        # If standing directly on food, or just wander / move towards coordinates
        pos = percept['agent_pos']
        # Simple heuristic or fallback random sweep
        return random.choice(self.actions_pool)

class SimpleReflexAgent:
    def sense_and_act(self, percept: dict) -> str:
        pass

class ModelBasedAgent:
    def sense_and_act(self, percept: dict) -> str:
        pass

class SearchAgent:
    """A problem-solving agent that uses uninformed search algorithms."""
    
    def __init__(self):
        self.plan = []
        self.active_algo = 'BFS'

    def sense_and_act(self, percept: dict) -> str:
        if not self.plan:
            agent_pos = tuple(percept['agent_pos'])
            all_food = percept.get('all_food', [])
            walls = percept.get('walls', [])
            grid_size = percept.get('grid_size', (4, 4))
            
            if not all_food:
                return 'Stay'
                
            closest_food = min(all_food, key=lambda f: abs(f[0] - agent_pos[0]) + abs(f[1] - agent_pos[1]))
            goal_pos = tuple(closest_food)
            
            if self.active_algo == 'BFS':
                self.plan = self.bfs_search(agent_pos, goal_pos, walls, grid_size)
            elif self.active_algo == 'DFS':
                self.plan = self.dfs_search(agent_pos, goal_pos, walls, grid_size)
            elif self.active_algo == 'UCS':
                self.plan = self.ucs_search(agent_pos, goal_pos, walls, grid_size)
                
            if not self.plan:
                return 'Stay'
                
        return self.plan.pop(0)

    def _get_successors(self, pos, walls, grid_size):
        x, y = pos
        width, height = grid_size
        successors = []
        
        # Actions matching the simulator
        if y + 1 < height and (x, y + 1) not in walls:
            successors.append(('Up', (x, y + 1), 1))
        if y - 1 >= 0 and (x, y - 1) not in walls:
            successors.append(('Down', (x, y - 1), 1))
        if x - 1 >= 0 and (x - 1, y) not in walls:
            successors.append(('Left', (x - 1, y), 1))
        if x + 1 < width and (x + 1, y) not in walls:
            successors.append(('Right', (x + 1, y), 1))
            
        return successors

    def bfs_search(self, start_pos, goal_pos, walls, grid_size):
        frontier = deque([(start_pos, [])])
        reached = {start_pos}
        
        while frontier:
            current_pos, path = frontier.popleft()
            
            if current_pos == goal_pos:
                return path
                
            for action, next_pos, cost in self._get_successors(current_pos, walls, grid_size):
                if next_pos not in reached:
                    reached.add(next_pos)
                    frontier.append((next_pos, path + [action]))
                    
        return []

    def dfs_search(self, start_pos, goal_pos, walls, grid_size):
        frontier = [(start_pos, [])]
        reached = set()
        
        while frontier:
            current_pos, path = frontier.pop()
            
            if current_pos == goal_pos:
                return path
            
            if current_pos not in reached:
                reached.add(current_pos)
                
                for action, next_pos, cost in self._get_successors(current_pos, walls, grid_size):
                    if next_pos not in reached:
                        frontier.append((next_pos, path + [action]))
                        
        return []

    def ucs_search(self, start_pos, goal_pos, walls, grid_size):
        frontier = [(0, start_pos, [])]
        reached = set()
        
        while frontier:
            current_cost, current_pos, path = heapq.heappop(frontier)
            
            if current_pos == goal_pos:
                return path
                
            if current_pos not in reached:
                reached.add(current_pos)
                
                for action, next_pos, step_cost in self._get_successors(current_pos, walls, grid_size):
                    if next_pos not in reached:
                        heapq.heappush(frontier, (current_cost + step_cost, next_pos, path + [action]))
                        
        return []
