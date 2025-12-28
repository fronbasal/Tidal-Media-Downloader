#!/usr/bin/env python
# -*- encoding: utf-8 -*-
"""
@File    :   pipHelper.py
@Time    :   2019/03/11
@Author  :   Yaronzz
@Version :   2.0
@Contact :   yaronhuang@foxmail.com
@Desc    :   pip server tool
"""

import tidal_dl.aigpy.netHelper as netHelper


def getInfo(projectName):
    """Get project information from pypi
    - Return: json or None
    """
    url = (
        "https://pypi.org/pypi/"
        + projectName
        + "/json"
    )
    # Try to get proxies from SETTINGS, but avoid circular import issues
    proxies = None
    try:
        from tidal_dl.settings import (
            SETTINGS,
        )

        proxies_dict = {}
        if (
            hasattr(
                SETTINGS, "httpProxy"
            )
            and SETTINGS.httpProxy
        ):
            proxies_dict["http"] = (
                SETTINGS.httpProxy
            )
        if (
            hasattr(
                SETTINGS, "httpsProxy"
            )
            and SETTINGS.httpsProxy
        ):
            proxies_dict["https"] = (
                SETTINGS.httpsProxy
            )
        proxies = (
            proxies_dict
            if proxies_dict
            else None
        )
    except:
        pass
    ret = netHelper.downloadJson(
        url, None, proxies=proxies
    )
    return ret


def getLastVersion(projectName):
    """Get project version from pypi
    - Return: str or None
    """
    try:
        ret = getInfo(projectName)
        if ret is None:
            return None
        return ret["info"]["version"]
    except:
        return None


def getVersionList(projectName):
    """Get project all versions from pypi
    - Return: json or None
    """
    try:
        ret = getInfo(projectName)
        if ret is None:
            return None
        return ret["releases"]
    except:
        return None
