from playwright.sync_api import sync_playwright as sync_playwright_default
from patchright.sync_api import sync_playwright as sync_playwright_stealth
from playwright.async_api import async_playwright as async_playwright_default
from patchright.async_api import async_playwright as async_playwright_stealth


def sync_playwright(stealth=True):
    if stealth:
        return sync_playwright_stealth()
    else:
        return sync_playwright_default()


def async_playwright(stealth=True):
    if stealth:
        return async_playwright_stealth()
    else:
        return async_playwright_default()


def is_stealth(obj):
    if isinstance(obj, type):
        cls = obj
    else:
        cls = obj.__class__
    return not cls.__module__.startswith('playwright')
