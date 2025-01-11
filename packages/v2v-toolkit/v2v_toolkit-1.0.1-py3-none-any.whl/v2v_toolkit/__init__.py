__version__ = "1.0.1"

__title__ = "v2v_toolkit"
__description__ = "Ver2Vision-Toolkit: Unified interface for streamlining 'Verbal Data to Vision Synthesis with Latent Diffusion Models' project. Provides tools for managing low-level downstream tasks."
__doc__ = __description__

__author__ = "Lukasz Michalski, Szymon Lopuszynski, Wojciech Rymer"
__email__ = "lukasz.michalski222@gmail.com"

__copyright__ = "Copyright (c) 2024 " + __author__

from .core.workspace import Workspace
from .core.graph import Graph
from .core.module import Module
from .core.context import Context
