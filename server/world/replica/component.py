"""
Component base
"""

class Component:
    """
    Component base class
    """
    def __init__(self, **kwargs):
        for prop, val in kwargs.items():
            setattr(self, prop, val)

    def write_construction(self, stream):
        raise NotImplementedError

    def serialize(self, stream):
        raise NotImplementedError
