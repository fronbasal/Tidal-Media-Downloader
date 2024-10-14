#!/usr/bin/env python
# -*- encoding: utf-8 -*-
"""
API client module - re-exports the existing TidalAPI implementation.

The core API functionality is implemented in tidal.py (TidalAPI class).
This module provides a clean interface for importing the API client.
"""

from tidal_dl.tidal import (
    TIDAL_API,
    TidalAPI,
)

__all__ = ["TidalAPI", "TIDAL_API"]
