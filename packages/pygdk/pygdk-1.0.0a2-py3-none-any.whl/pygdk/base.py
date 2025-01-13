from .surface import Surface

def init(width: int, height: int) -> Surface:
    surface = Surface((width, height))
    return surface