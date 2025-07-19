"""
Function Router Module (Legacy)

This module provides backward compatibility with the old FunctionRouter interface.
For new projects, use core.tool_manager.ToolManager instead.
"""

import warnings
from core.tool_manager import FunctionRouter

# Issue deprecation warning
warnings.warn(
    "function_router module is deprecated. Use core.tool_manager instead.",
    DeprecationWarning,
    stacklevel=2
)

# Export for backward compatibility
__all__ = ["FunctionRouter"] 
    