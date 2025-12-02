from smolagents import Tool
import kociemba

# Note: This script requires the 'kociemba' Python package.
# Install it using: pip install kociemba

class RubiksCubeSolver(Tool):
    name = "rubiks_cube_solver"
    description = (
            "This is a rubiks cube solver, using Kociemba's two stage solver package"
            "Required is a 54 character string representing a rubiks cube state in the format (URFDLB)"
            )
    input = {
            "state": {
                "type": "string",
                "description": "The 54-character string representing the Rubik's Cube state."
                }
            }
    output_type = "string"
    
    def forward(self,state: str) -> str:

        try:
            # 3. Call the Kociemba solver
            # The solve() function handles all the internal logic and returns the solution string.
            solution = kociemba.solve(cube_state)
            return solution
        
        except ValueError as e:
            # The kociemba library raises a ValueError if the cube state is invalid (e.g.,
            # wrong number of stickers per color, or physically unsolvable parity/orientation).
            return f"Error: The provided cube state is invalid or unsolvable. Details: {e}"
        except Exception as e:
            # Handle unexpected errors
            return f"An unexpected error occurred during solving: {e}"
