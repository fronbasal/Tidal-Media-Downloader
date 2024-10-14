#!/usr/bin/env python
# -*- encoding: utf-8 -*-
"""
Tidal-DL - Download music and videos from Tidal

Refactored codebase maintaining 100% CLI compatibility with original.
"""

__version__ = "2025.10"

# Re-export main entry point
from tidal_dl.main import main

__all__ = ["main"]
