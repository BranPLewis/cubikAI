try:
    from smolagents import Tool
except Exception:
    Tool = object

POS_CHARACTERS = "UDLRBF"
COLOR_CHARACTERS = "YWGBOR"

# Face order used by many cube libraries for a 54-char string:
# faces are ordered: U, R, F, D, L, B (each 9 chars)
POS_ORDER = ["U", "R", "F", "D", "L", "B"]


class RubiksCubeStringVerifier(Tool):
    name = "Rubiks_Cube_String_Verifier"
    description = (
        """
        Tool to verify and convert Rubik's Cube state strings between positional
        notation (U,D,L,R,B,F) and color-letter notation (Y,W,G,B,R,O).
        Detection of which color corresponds to which face is done by reading
        the center (5th) character of each 9-character face block.
        """
    )
    inputs = {
        "state": {
            "type": "string",
            "description": "The 54-character string representing the Rubik's Cube state."
        }
    }
    output_type = "string"

    def __init__(self):
        super().__init__()

    def is_valid_pos(self, state: str) -> bool:
        state = ''.join(state.split()).upper()
        if not isinstance(state, str) or len(state) != 54:
            return False
        # each position character should be one of the allowed and appear exactly 9 times
        for ch in state:
            if ch not in POS_CHARACTERS:
                return False
        # count check
        counts = {c: state.count(c) for c in POS_CHARACTERS}
        return all(counts[c] == 9 for c in POS_CHARACTERS)

    def is_valid_color(self, state: str) -> bool:
        state = ''.join(state.split()).upper()
        if not isinstance(state, str) or len(state) != 54:
            return False
        # all chars must be one of the color letters
        for ch in state:
            if ch not in COLOR_CHARACTERS:
                return False
        # each color should appear exactly 9 times in a valid cube coloring
        counts = {c: state.count(c) for c in COLOR_CHARACTERS}
        return all(counts[c] == 9 for c in COLOR_CHARACTERS)
    def _derive_mapping_from_color_state(self, state: str) -> dict:
        """Derive a mapping from position letter -> color letter by reading
        the center (index 4) of each 9-character face block. Face order is
        assumed to be U, R, F, D, L, B in the string.
        Returns a dict mapping position letter (U/R/F/D/L/B) -> color letter.
        """
        s = ''.join(state.split()).upper()
        if len(s) != 54:
            raise ValueError("Color state must be a 54-character string")
        mapping = {}
        centers = []
        for i, pos in enumerate(POS_ORDER):
            face = s[i * 9:(i + 1) * 9]
            center = face[4]
            mapping[pos] = center
            centers.append(center)
        # basic sanity: centers should be 6 distinct colors
        if len(set(centers)) != 6:
            raise ValueError("Invalid cube: face centers are not all distinct")
        return mapping

    def pos_to_color(self, state: str, color_reference: str = None, default_mapping: dict = None) -> str:
        """Convert a 54-char positional string (letters U,R,F,D,L,B) to a
        54-char color string.
        """
        s = ''.join(state.split()).upper()
        if not isinstance(s, str) or len(s) != 54:
            raise ValueError("Input must be a 54-character string of U,R,F,D,L,B")
        pos_to_color_map = {
            'U': state[4],
            'R': state[13],
            'F': state[22],
            'D': state[31],
            'L': state[40],
            'B': state[49]
        }
        out_chars = []
        for ch in s:
            if ch not in pos_to_color_map:
                raise ValueError(f"Unexpected character in positional input: {ch}")
            out_chars.append(pos_to_color_map[ch])
        return ''.join(out_chars)

    def color_to_pos(self, state: str) -> str:
        """Convert a 54-char color-letter string to positional letters by
        detecting which color is on which face via face centers.
        """
        s = ''.join(state.split()).upper()
        if not isinstance(s, str) or len(s) != 54:
            raise ValueError("Input must be a 54-character color-letter string")
        if not self.is_valid_color(s):
            raise ValueError("Input is not a valid color string (invalid chars/counts)")
        pos_to_color = self._derive_mapping_from_color_state(s)
        # invert mapping: color -> pos
        color_to_pos_map = {c: p for p, c in pos_to_color.items()}
        out_chars = []
        for ch in s:
            if ch not in color_to_pos_map:
                raise ValueError(f"Unexpected character in color input: {ch}")
            out_chars.append(color_to_pos_map[ch])
        return ''.join(out_chars)

    def forward(self, state: str) -> str: 
        """
        The main execution method for the tool.
        It takes the 'state' string and performs a verification or conversion.
        """
        if self.is_valid_pos(state):
            return self.pos_to_color(state)
        elif self.is_valid_color(state):
            return state
        else:
            return "Error: Input state is neither a valid positional nor color-letter string (54 characters of UDLRBF or YWGBOR required)."
        
v = RubiksCubeStringVerifier()

print(v.color_to_pos("WWRWWWGWRBRBOROGRYWGYRGGWGYOYROYGOYGGORROYBBBWBOYBBOBY"))