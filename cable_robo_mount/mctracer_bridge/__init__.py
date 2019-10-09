from . import merlict_json
from . import star_light_analysis
from sys import platform
if platform == "win32":
    from .RayTracingMachine import RayTracingMachine
