"""
Gets all replica classes from other modules to provide at top level

Core concept via https://stackoverflow.com/a/25562415/
"""

from .base_data import BaseData
from .component import Component

from server.plugin import Plugin, get_derivatives

for component in get_derivatives(__package__, Component):
    locals()[component.__name__] = component