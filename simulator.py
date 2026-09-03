# simulator.py
from grid_game import GridHuntGame
from agent import GreedyGridAgent, SearchAgent

def run_grid_hunt():
    print("=== UC Berkeley Style Small Grid Hunt Started ===")
    
    for algo in ['BFS', 'DFS', 'UCS']:
        print(f"\n--- Running with {algo} ---")
        env = GridHuntGame()
        agent = SearchAgent()
        agent.active_algo = algo
        
        while not env.is_done():
            percept = env.get_percept(agent)
            action = agent.sense_and_act(percept)
            env.execute_action(agent, action)
            print(f"Pos: {percept['agent_pos']} | Action: {action} | Food Left: {percept['remaining_food']} | Score: {percept['score']}")

        print(f"Game Over! Final Score: {env.score} after {env.steps} steps.")

if __name__ == "__main__":
    run_grid_hunt()