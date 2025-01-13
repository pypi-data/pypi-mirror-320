from . import is_stealth
from .errors import async_safe_process, async_raise, sync_safe_process, sync_raise

page_content_messages = [
    "Page.content: Unable to retrieve content because the page is navigating and changing the content."
]


async def async_page_content(page):
    async def main():
        return await page.content()

    return await async_safe_process(main, others=async_raise, stealth=is_stealth(page), messages=page_content_messages)


def sync_page_content(page):
    def main():
        return page.content()

    return sync_safe_process(main, others=sync_raise, stealth=is_stealth(page), messages=page_content_messages)
