import os
import json
from ..file import read_file, write_file
from ..web.url import Url
from . import is_stealth
from .errors import async_safe_process, sync_safe_process, async_none, sync_none


class PlaywrightState:
    js_storages = """
    () => {
        function dump(storage) {
            var result = {};
            for (var i = 0; i < storage.length; i++) {
                var k = storage.key(i)
                var v = storage.getItem(k)
                result[k] = v
            }
            return result
        }

        return JSON.stringify([
            dump(localStorage),
            dump(sessionStorage),
        ])
    }
    """
    ignore_messages = [
        "Page.evaluate: SecurityError: Failed to read the 'localStorage' property from 'Window'",
        "Page.evaluate: Execution context was destroyed, most likely because of a navigation."
    ]

    @classmethod
    async def context_dump(cls, context):
        async def main():
            local, session = json.loads(await page.evaluate(cls.js_storages))
            all_local[page.url] = local
            all_session[page.url] = session

        stealth = is_stealth(context)
        all_local = {}
        all_session = {}
        for page in context.pages:
            await async_safe_process(main, message=async_none, messages=cls.ignore_messages, stealth=stealth)
        cookies = await context.cookies()
        return [all_local, all_session, cookies]

    @classmethod
    def sync_context_dump(cls, context):
        def main():
            local, session = json.loads(page.evaluate(cls.js_storages))
            all_local[page.url] = local
            all_session[page.url] = session

        stealth = is_stealth(context)
        all_local = {}
        all_session = {}
        for page in context.pages:
            sync_safe_process(main, message=sync_none, messages=cls.ignore_messages, stealth=stealth)
        cookies = context.cookies()
        return [all_local, all_session, cookies]

    def __init__(self, path=None):
        self.path = path
        self.local_storage = {}
        self.session_storage = {}
        self.cookies = {}
        self.load_file()

    def load_file(self):
        if self.path and os.path.isfile(self.path):
            self.load_data(json.loads(read_file(self.path)))

    def load_data(self, data):
        if data:
            self.local_storage = data[0]
            self.session_storage = data[1]
            self.cookies = data[2]

    def dump_data(self):
        return [self.local_storage, self.session_storage, self.cookies]

    async def assign_context(self, context, *args, **kwargs):
        await context.add_cookies(self.context_cookies)
        await context.add_init_script(script=self.get_page_init_script(*args, **kwargs))

    def sync_assign_context(self, context, *args, **kwargs):
        context.add_cookies(self.context_cookies)
        context.add_init_script(script=self.get_page_init_script(*args, **kwargs))

    async def update_from_context(self, context):
        self.update(*await self.context_dump(context))

    def sync_update_from_context(self, context):
        self.update(*self.sync_context_dump(context))

    def update(self, local_storage, session_storage, cookies):
        dirty = False
        for url, data in local_storage.items():
            origin = Url.new(url).origin.value
            current = self.local_storage.get(origin, {})
            if data != current:
                dirty = True
                if data:
                    self.local_storage[origin] = data
                else:
                    self.local_storage.pop(origin, None)
        for url, data in session_storage.items():
            url = Url.new(url).fixed
            current = self.session_storage.get(url, {})
            if data != current:
                dirty = True
                if data:
                    self.session_storage[url] = data
                else:
                    self.session_storage.pop(url, None)
        cookies = {json.dumps(data, sort_keys=True): data for data in cookies}
        if self.cookies != cookies:
            dirty = True
            self.cookies = cookies
        if dirty and self.path:
            write_file(self.path, json.dumps(
                [self.local_storage, self.session_storage, self.cookies]
                , ensure_ascii=False))

    def get_page_init_script(self, once=True):
        return """
        (function(data) {
            function load(storage, d) {
                storage.clear()
                for (var property in d) {
                    if (d.hasOwnProperty(property)) {
                        storage.setItem(property, d[property])
                    }
                }
            }

            if (localStorage.length === 0 || !data.once)
                load(localStorage, data.local[window.origin] || {})
            var url = new URL(window.location)
            url.searchParams.sort()
            load(sessionStorage, data.session[url.href] || {})
        })(%s)
        """ % json.dumps({
            'local': self.local_storage,
            'session': self.session_storage,
            'once': once
        })

    @property
    def context_cookies(self):
        return list(self.cookies.values())
