import random
import math
from collections import deque
import heapq
from logic_engine import KnowledgeBase


class GreedyGridAgent:
    """Original Lab 1 random agent."""

    def __init__(self):
        self.actions_pool = ['Up', 'Down', 'Left', 'Right']

    def sense_and_act(self, percept: dict) -> str:
        return random.choice(self.actions_pool)



class SimpleReflexAgent:
    """
    Simple Reflex Agent.
    Uses only the current percept.
    Does not maintain memory/history.
    """

    def sense_and_act(self, percept: dict) -> str:

        # IF food_here THEN Suck and collect food
        if percept["food_here"]:
            return "Suck"

        # IF wall_ahead THEN turn left
        elif percept["wall_ahead"]:
            return "Left"

        # ELSE move forward
        else:
            return "Up"

class ModelBasedAgent:

    def __init__(self):
        self.visited_positions = set()
        self.last_action = None
        self.actions = ["Up", "Right", "Down", "Left"]


    def sense_and_act(self, percept):

        current_position = tuple(percept["agent_pos"])

        self.visited_positions.add(current_position)


        # If food exists
        if percept["food_here"]:
            self.last_action = "Suck"
            return "Suck"
        # If toxin detected, avoid staying
        if percept["smells_toxin"]:
            self.last_action = "Right"
            return "Right"

        # If wall ahead, choose another direction
        if percept["wall_ahead"]:

            for action in self.actions:

                if action != self.last_action:
                    self.last_action = action
                    return action


        # Normal exploration
        for action in self.actions:

            if action == self.last_action:
                continue


            if action == "Up":
                next_position = (
                    current_position[0],
                    current_position[1] + 1
                )

            elif action == "Down":
                next_position = (
                    current_position[0],
                    current_position[1] - 1
                )

            elif action == "Left":
                next_position = (
                    current_position[0] - 1,
                    current_position[1]
                )

            else:
                next_position = (
                    current_position[0] + 1,
                    current_position[1]
                )


            if next_position not in self.visited_positions:
                self.last_action = action
                return action


        # If all visited, move differently
        self.last_action = "Right"
        return "Right"

    
class SearchAgent:
    """Goal-Based/Planning Agent using BFS, DFS, and UCS."""

    def __init__(self):
        self.plan = []
        self.active_algo = 'AStar'
        # Create Knowledge Base
        self.kb = KnowledgeBase()

        # Rule 1:
        # TargetVisible AND HasDust -> SafeToEngage
        self.kb.tell_rule(
            ['TargetVisible', 'HasDust'],
            'SafeToEngage'
        )

        # Rule 2:
        # SafeToEngage AND BloodseekerMissing -> Retreat
        self.kb.tell_rule(
            ['SafeToEngage', 'BloodseekerMissing'],
            'Retreat'
        )

    def manhattan_distance(self, pos, goal):
        """Calculate Manhattan distance between two positions."""
        return abs(pos[0] - goal[0]) + abs(pos[1] - goal[1])

    def euclidean_distance(self, pos, goal):
        """Calculate Euclidean distance between two positions."""
        return math.sqrt(
            (pos[0] - goal[0]) ** 2 +
            (pos[1] - goal[1]) ** 2
        )

    def get_successors(self, state, percept):
        """Generate valid neighbouring states and their actions."""

        x, y = state
        width, height = percept["grid_size"]
        walls = set(percept["walls"])

        moves = [
            ("Up", (x, y + 1)),
            ("Right", (x + 1, y)),
            ("Down", (x, y - 1)),
            ("Left", (x - 1, y))
        ]

        successors = []

        for action, new_position in moves:
            nx, ny = new_position

            if 0 <= nx < width and 0 <= ny < height:
                if new_position not in walls:
                    successors.append((new_position, action))

        return successors

    def find_closest_food(self, start_pos, food_positions):
        """Find the closest food using Manhattan distance."""

        if not food_positions:
            return None

        return min(
            food_positions,
            key=lambda food:
                abs(start_pos[0] - food[0]) +
                abs(start_pos[1] - food[1])
        )

    def bfs_search(self, start, goal, percept):
        """Breadth-First Search."""

        frontier = deque([(start, [])])
        reached = {start}

        while frontier:
            current, path = frontier.popleft()

            if current == goal:
                return path

            for next_position, action in self.get_successors(
                current, percept
            ):
                if next_position not in reached:
                    reached.add(next_position)
                    frontier.append(
                        (next_position, path + [action])
                    )

        return []

    def dfs_search(self, start, goal, percept):
        """Depth-First Search."""

        frontier = [(start, [])]
        reached = {start}

        while frontier:
            current, path = frontier.pop()

            if current == goal:
                return path

            for next_position, action in self.get_successors(
                current, percept
            ):
                if next_position not in reached:
                    reached.add(next_position)
                    frontier.append(
                        (next_position, path + [action])
                    )

        return []

    def ucs_search(self, start, goal, percept):
        """Uniform-Cost Search."""

        frontier = []
        counter = 0

        heapq.heappush(
            frontier,
            (0, counter, start, [])
        )

        reached = {start: 0}

        while frontier:
            cost, _, current, path = heapq.heappop(frontier)

            if current == goal:
                return path

            if cost > reached.get(current, float('inf')):
                continue

            for next_position, action in self.get_successors(
                current, percept
            ):
                new_cost = cost + 1

                if (
                    next_position not in reached
                    or new_cost < reached[next_position]
                ):
                    reached[next_position] = new_cost
                    counter += 1

                    heapq.heappush(
                        frontier,
                        (
                            new_cost,
                            counter,
                            next_position,
                            path + [action]
                        )
                    )

        return []

    def astar_search(
        self,
        start_pos,
        goal_pos,
        percept,
        heuristic_type="manhattan"
    ):
        """A* Search using f(n) = g(n) + h(n)."""

        frontier = []
        counter = 0

        # Calculate initial heuristic
 
        if heuristic_type == "manhattan":
            h_cost = self.manhattan_distance(
                start_pos,
                goal_pos
            )
        else:
            h_cost = self.euclidean_distance(
                start_pos,
                goal_pos
            )

        # (f_cost, g_cost, counter, position, path)
        heapq.heappush(
            frontier,
            (
                h_cost,
                0,
                counter,
                start_pos,
                []
            )
        )

        reached = {start_pos: 0}

        while frontier:

            f_cost, g_cost, _, current, path = heapq.heappop(
                frontier
            )

            if current == goal_pos:
                return path

            if g_cost > reached.get(
                current,
                float('inf')
            ):
                continue

            for next_position, action in self.get_successors(
                current,
                percept
            ):

                # Check Knowledge Base for this tile
                self.kb.clear_facts()

                # Add TargetVisible fact
                if next_position in percept["all_food"]:
                    self.kb.tell_fact("TargetVisible")

                # Add HasDust fact
                if next_position not in percept["walls"]:
                    self.kb.tell_fact("HasDust")

                # Add BloodseekerMissing fact if available
                if percept.get("bloodseeker_missing", False):
                    self.kb.tell_fact("BloodseekerMissing")

                # Run Forward Chaining
                self.kb.forward_chain()

                # Skip tile if Retreat is deduced
                if "Retreat" in self.kb.facts:
                    continue


                new_g_cost = g_cost + 1

                if (
                    next_position not in reached
                    or new_g_cost < reached[next_position]
                ):

                    reached[next_position] = new_g_cost

                    # Calculate heuristic
                    if heuristic_type == "manhattan":
                        h_cost = self.manhattan_distance(
                            next_position,
                            goal_pos
                        )
                    else:
                        h_cost = self.euclidean_distance(
                            next_position,
                            goal_pos
                        )

                    # f(n) = g(n) + h(n)
                    new_f_cost = new_g_cost + h_cost

                    counter += 1

                    heapq.heappush(
                        frontier,
                        (
                            new_f_cost,
                            new_g_cost,
                            counter,
                            next_position,
                            path + [action]
                        )
                    )

        return []

    def sense_and_act(self, percept):
        """Create and execute a plan toward the closest food."""

        if percept["food_here"]:
            self.plan = []
            return "Suck"

        if not self.plan:

            start = tuple(percept["agent_pos"])

            food_positions = [
                tuple(food)
                for food in percept["all_food"]
            ]

            goal = self.find_closest_food(
                start,
                food_positions
            )

            if goal is None:
                return "Suck"

            if self.active_algo == "BFS":
                self.plan = self.bfs_search(
                    start, goal, percept
                )

            elif self.active_algo == "DFS":
                self.plan = self.dfs_search(
                    start, goal, percept
                )

            elif self.active_algo == "UCS":
                self.plan = self.ucs_search(
                    start, goal, percept
                )

            elif self.active_algo == "AStar":
                self.plan = self.astar_search(
                    start, goal, percept
                )

        if self.plan:
            return self.plan.pop(0)

        return "Suck"
    
if __name__ == "__main__":
      agent = SearchAgent()

      print("Manhattan Distance:", agent.manhattan_distance((0, 0), (3, 4)))
      print("Euclidean Distance:", agent.euclidean_distance((0, 0), (3, 4)))