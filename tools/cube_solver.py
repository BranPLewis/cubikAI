import os
import shutil
import subprocess
import re
from typing import List, Dict, Any
from smolagents import Tool

class RubiksCubeSolver(Tool):
    name = "Rubiks_Cube_Solver"
    description = (
        """
        A beginner-friendly Rubik's Cube solver that provides step-by-step instructions 
        using a local C/C++ solver executable.
        Input must be a 54-character facelet string in the order U-R-F-D-L-B.
        """
    )

    inputs = {
        "cube_state": {
            "type": "string",
            "description": (
                "The state of the rubiks cube in a 54 character format in the order U-R-F-D-L-B "
                "(Up, Right, Front, Down, Left, Back)."
            ),
        }
    }
    output_type = "string"

    def __init__(self, c_solver_path: str = "") -> None:
        """If `c_solver_path` is not provided, the tool looks for an executable at
        `./rubiks-cube-solver/bin/rubiks-cube-solver` or the path given by the
        environment variable `RUBIKS_C_SOLVER_PATH`.
        """
        self.c_solver_path = c_solver_path or os.environ.get("RUBIKS_C_SOLVER_PATH")
        if not self.c_solver_path:
            self.c_solver_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "rubiks-cube-solver", "bin", "rubiks-cube-solver")

    def _find_c_solver(self) -> str:
        """Return path to C solver executable if it exists, else empty string."""
        if self.c_solver_path and os.path.isfile(self.c_solver_path) and os.access(self.c_solver_path, os.X_OK):
            return self.c_solver_path
        exe = shutil.which("rubiks-cube-solver")
        return exe if exe else ""

    def _parse_solution_from_output(self, out: str) -> str:
        """Extract the move sequence from solver output."""
        for line in out.splitlines():
            if "Solution:" in line:
                return line.split("Solution:")[1].strip()
        m = re.search(r"([URFDLBurfdlMESxyz0-9'\\s]+)$", out)
        if m:
            return m.group(1).strip()
        return ""

    def _solve_subgoal(self, cube_state: str, goal_state: str) -> str:
        """Calls the C solver to solve a specific subgoal."""
        c_solver = self._find_c_solver()
        if not c_solver:
            return "Error: C solver not found."

        u_face, r_face, f_face, d_face, l_face, b_face = [cube_state[i:i+9] for i in range(0, 54, 9)]
        solver_cube_state = u_face + l_face + f_face + r_face + b_face + d_face

        u_goal, r_goal, f_goal, d_goal, l_goal, b_goal = [goal_state[i:i+9] for i in range(0, 54, 9)]
        solver_goal_state = u_goal + l_goal + f_goal + r_goal + b_goal + d_goal
        
        commands = f"init cube {solver_cube_state}\ninit goal {solver_goal_state}\nsearch tree astar\nexit\n"
        
        proc = None
        try:
            proc = subprocess.Popen([c_solver], stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
            out, err = proc.communicate(commands, timeout=60)
            if proc.returncode != 0 and not out:
                return f"Error: C solver failed. stderr: {err.strip()}"
            solution = self._parse_solution_from_output(out)
            return solution if solution else f"Error: No solution found for subgoal. Output:\n{out.strip() or err.strip()}"
        except subprocess.TimeoutExpired:
            if proc:
                proc.kill()
            return "Error: C solver timed out."
        except Exception as e:
            return f"Error: {e}"

    def forward(self, cube_state: str) -> str:
        if not isinstance(cube_state, str) or len(cube_state) != 54:
            return "Error: Cube string must be a 54-character string."

        subgoals = self.get_subgoals()
        full_solution = []
        current_state = cube_state

        for i, subgoal in enumerate(subgoals):
            goal_state = self.create_goal_state(subgoal['mask'], current_state)
            step_solution = self._solve_subgoal(current_state, goal_state)
            
            if "Error:" in step_solution:
                return f"Failed at step {i+1} ({subgoal['name']}): {step_solution}"
            
            full_solution.append(f"Step {i+1}: {subgoal['name']}\n  Algorithm: {step_solution}\n")
            current_state = self.apply_moves(current_state, step_solution)

        return "\n".join(full_solution)

    def get_subgoals(self) -> List[Dict[str, Any]]:
        return [
            {"name": "White Cross", "mask": "w**w*w**w" + "*"*9 + "*"*9 + "*"*9 + "*"*9 + "*"*9},
            {"name": "First Layer Corners", "mask": "wwwwwwwww" + "g"*9 + "r"*9 + "b"*9 + "o"*9 + "y"*9},
            # Add more subgoals for other layers
        ]

    def create_goal_state(self, mask: str, current_state: str) -> str:
        goal_state = ""
        for i in range(54):
            goal_state += current_state[i] if mask[i] == '*' else mask[i]
        return goal_state

    def apply_moves(self, cube_state: str, moves: str) -> str:
        # This is a placeholder. A real implementation would need a cube model 
        # to apply the moves and return the new state.
        # For now, we'll assume the solver gives us the state after the moves.
        # This part needs to be implemented for a fully working step-by-step solver.
        print(f"Applying moves: {moves} (simulation not implemented)")
        return cube_state

if __name__ == '__main__':
    solver = RubiksCubeSolver()
    scrambled_cube_urf_format = "rbyogywrowgbbwroywgyrybrwogwobyrgwybwoogrbgyryowobg"
    solution = solver.forward(scrambled_cube_urf_format)
    print(f"Step-by-step solution:\n{solution}")