import re, sys, time  # noqa E401
from enum import Enum
from typing import List, Optional, Union, Tuple

SUPPORTED_PLATFORMS = ["linux", "win32", "darwin"]


class ANSINotSupportedError(Exception):
    def __init__(self, platform):
        super().__init__(f"ANSI colors are not supported on platform: {platform}")


class Colors(Enum):
    def __str__(self):
        if not any(sys.platform.startswith(platform) for platform in SUPPORTED_PLATFORMS):
            raise ANSINotSupportedError(f"ANSI colors are not supported on platform: {sys.platform}")
        return self.value

    # Foreground colors
    RED = "\033[38;5;124m"
    GREEN = "\033[92m"
    BLUE = "\033[94m"
    BLACK = "\033[30m"
    WHITE = "\033[97m"
    GREY = "\033[90m"
    LIGHT_RED = "\033[91m"
    LIGHT_BLUE = "\033[94m"
    LIGHT_GREEN = "\033[92m"
    YELLOW = "\033[93m"
    ORANGE = "\033[38;5;214m"
    CYAN = "\033[96m"
    MAGENTA = "\033[95m"

    # Background colors
    RED_BG = "\033[48;5;124m"
    GREEN_BG = "\033[42m"
    BLUE_BG = "\033[44m"
    BLACK_BG = "\033[40m"
    WHITE_BG = "\033[48;5;15m"
    GREY_BG = "\033[48;5;8m"
    LIGHT_RED_BG = "\033[48;5;9m"
    LIGHT_BLUE_BG = "\033[48;5;12m"
    LIGHT_GREEN_BG = "\033[48;5;10m"
    YELLOW_BG = "\033[48;5;11m"
    ORANGE_BG = "\033[48;5;214m"
    CYAN_BG = "\033[46m"
    MAGENTA_BG = "\033[45m"

    BOLD = "\033[1m"
    ITALIC = "\033[3m"
    UNDERLINE = "\033[4m"
    STRIKETHROUGH = "\033[9m"
    FRAME = "\033[51m"

    RESET = "\033[0m"

    @classmethod
    def available_colors(cls) -> str:
        """Print all available colors and styles with their names."""
        for color in cls:
            print(f"{color.value}{color.name}{Colors.RESET}")
        return ""


_pre_colors = {
    # foreground, background
    "red": ["\033[38;5;124m", "\033[48;5;124m"],
    "green": ["\033[92m", "\033[42m"],
    "blue": ["\033[94m", "\033[44m"],
    "black": ["\033[30m", "\033[40m"],
    "white": ["\033[97m", "\033[48;5;15m"],
    "grey": ["\033[90m", "\033[48;5;8m"],
    "light_red": ["\033[91m", "\033[48;5;9m"],
    "light_blue": ["\033[94m", "\033[48;5;12m"],
    "light_green": ["\033[92m", "\033[48;5;10m"],
    "yellow": ["\033[93m", "\033[48;5;11m"],
    "orange": ["\033[38;5;214m", "\033[48;5;214m"],
    "cyan": ["\033[96m", "\033[46m"],
    "magenta": ["\033[95m", "\033[45m"],

    # Text formatting
    "bold": ["\033[1m", "\033[1m"],
    "italic": ["\033[3m", "\033[3m"],
    "underline": ["\033[4m", "\033[4m"],
    "strikethrough": ["\033[9m", "\033[9m"],
    "frame": ["\033[51m", "\033[51m"],

    # Reset
    "reset": ["\033[0m", "\033[0m"]
}


def _predefined_color_check(color: str) -> List[Optional[str]]:
    """
    Check if color exists in predefined colors
    :param color: Color to check. Valid color should be any of the keys in COLORS dictionary (red, green...)
    :return: Ansi color codes from predefined colors
    """
    if color in _pre_colors:
        return _pre_colors[color]
    return []  # return empty list if color does not exist


def _hex_to_rgb(hex_color: str) -> Union[List, Tuple]:
    """
    Convert a HEX color to an RGB tuple.
    :returns: Tuple of RGB values or List contains two values (fg, bg) from predefined colors. Else return empty tuple
    """
    if hex_color is None:
        return ()

    if not hex_color.startswith('#'):
        # Return list contains two values (fg, bg) from predefined colors
        return _predefined_color_check(hex_color) if hex_color in _pre_colors else ()

    hex_color = hex_color.lstrip('#')
    return tuple(int(hex_color[i:i + 2], 16) for i in (0, 2, 4))


def _rgb_to_ansi(rgb_color: Union[List, Tuple], is_foreground: bool) -> Union[List, str]:
    """
    Convert an RGB tuple to ANSI code.
    :param rgb_color: RGB tuple. If it's a list, it must be a list contains two values (fg, bg)
    :param is_foreground: return flag for foreground or background. will be ignored if rgb_color is a list
    :return:
    """
    if not rgb_color:
        return ""

    if isinstance(rgb_color, list):
        # immediately return the rgb_color if it's a list (valid fg and bg ansi code from predefined colors)
        return rgb_color

    r, g, b = rgb_color
    if is_foreground:
        return f"\033[38;2;{r};{g};{b}m"
    else:
        return f"\033[48;2;{r};{g};{b}m"


def _replacer(match):
    # Check if the match is a valid foreground or background color or a valid hex code
    color_key = match.group(1) or match.group(2)

    # If it's a valid color key from the dictionary
    color = _predefined_color_check(color_key)
    if color:
        # Determine whether it's a foreground or background color
        return color[0] if match.group(1) else color[1]

    # If it's a hex color (either foreground or background), convert it to ANSI code
    if color_key.startswith("#"):
        rgb = _hex_to_rgb(color_key)
        if match.group(1):  # Foreground color
            return _rgb_to_ansi(rgb, is_foreground=True)
        else:  # Background color
            return _rgb_to_ansi(rgb, is_foreground=False)

    # If it's neither a valid color nor a valid hex, return the match as-is (no change)
    return match.group(0)


def color_print(
        text=None,
        print_time: bool = True,
        fg: str = None,
        bg: str = None,
        bold: bool = False,
        italic: bool = False,
        underline: bool = False,
        strikethrough: bool = False,
        frame: bool = False
) -> None:
    """
    Print colored text to the console with optional styling.

    This function allows printing text with customizable foreground and background colors, as well as
    additional styles like bold, italic, etc.

    NOTE: If `fg`, `bg`, or any of the styling arguments are specified, any inline color codes or styles
    embedded within the text will be overridden.

    :param text: The text to print (supports any type that can be converted to a string).
    :param fg: Foreground color in HEX format (e.g., "#ff0000").
    :param bg: Background color in HEX format (e.g., "#0000ff").
    :param bold: Apply bold text.
    :param italic: Apply italic text.
    :param underline: Underline the text.
    :param strikethrough: Strike through the text.
    :param frame: Add a frame around the text.
    :param print_time: Prepend the current time (HH:MM) to the text.
    :raises ANSINotSupportedError: Raised if the platform does not support ANSI escape codes.
    :return: None

    Example:
    --------
    >>> # Print text with a red foreground color and bold styling using inline tags
    >>> color_print("[red][bold]Hello, World![reset]")

    >>> # Print text with a custom purple background and italic styling
    >>> # Use double brackets `[[ ]]` for background colors
    >>> color_print("[[#d143b8]]Hello[reset], [cyan][italic]World![reset]")

    >>> # Print text with function arguments (overriding inline tags)
    >>> color_print("Hello, World!", fg="cyan", bold=True, frame=True)

    >>> # Print text exactly as written, including inline tags
    >>> # Use exclamation marks `!` to mark it as ignored styling
    >>> color_print("My favorite color is [!#ff0000] and [!blue]")
    """

    if not any(sys.platform.startswith(platform) for platform in SUPPORTED_PLATFORMS):
        raise ANSINotSupportedError(sys.platform)

    ptn = re.compile(r"\[(!?[a-z_]+|#[0-9a-fA-F]{6})]|\[\[(!?[a-z_]+|#[0-9a-fA-F]{6})]]")
    styled_text = ptn.sub(_replacer, text)
    curr_time = f"\033[46m\033[30m {time.strftime('%H:%M')} \033[0m " if print_time else ""

    if fg or bg or bold or italic or underline or strikethrough or frame:
        rgb_fg, rgb_bg = _hex_to_rgb(fg), _hex_to_rgb(bg)
        fg_ansi, bg_ansi = _rgb_to_ansi(rgb_fg, is_foreground=True), _rgb_to_ansi(rgb_bg, is_foreground=False)
        fg_color = fg_ansi[0] if isinstance(fg_ansi, list) else fg_ansi
        bg_color = bg_ansi[1] if isinstance(bg_ansi, list) else bg_ansi
        s1 = _pre_colors["bold"][0] if bold else "" + _pre_colors["italic"][0] if italic else ""
        s2 = _pre_colors["underline"][0] if underline else "" + _pre_colors["strikethrough"][0] if strikethrough else ""
        s3 = _pre_colors["frame"][0] if frame else ""
        print(f"{curr_time}{fg_color}{bg_color}{s1}{s2}{s3}{text}\033[0m")
    else:
        print(curr_time + styled_text)
