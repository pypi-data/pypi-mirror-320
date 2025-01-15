# https://github.com/Kaliiiiiiiiii-Vinyzu/patchright-python/issues/9
import copy
import os
import random
import string

from ..str import Fragment
from ..web.headers import quick_split_ct


class RouteTool:
    random_length = 64

    def __init__(self, is_stealth):
        self.is_stealth = is_stealth
        if self.is_stealth:
            char_set = string.digits + string.ascii_letters
            self.uid = ''.join(random.choice(char_set) for _ in range(self.random_length))

    async def _error_add_script(self, *args, **kwargs):
        raise ValueError('No more add_init_script should be called')

    async def finally_add_script(self, context):
        if self.is_stealth:
            await context.add_init_script(script="//" + self.uid)
            context.add_init_script = self._error_add_script

    @classmethod
    def fix_package(cls, reverse=False):
        import patchright
        from ..file import read_text, write_file
        path_file = os.path.join(
            os.path.dirname(os.path.abspath(patchright.__file__)),
            'driver/package/lib/server/chromium/crNetworkManager.js'
        )
        content = read_text(path_file)
        replace = [
            [
                "const isTextHtml = response.headers.some(header => header.name === 'content-type' && "
                "header.value.includes('text/html'));",
                """const index = response.headers.findIndex(header => header.name == '--add-script-inject--' && header.value == 'true');
let isTextHtml = false
if (index !== -1){
  response.headers.splice(index, 1)
  isTextHtml = true
}"""],
            ["        injectionHTML += `<script", "        if(isTextHtml)injectionHTML += `<script"]
        ]
        content = Fragment.replace_safe_again(content, replace, reverse)
        if content is not None:
            write_file(path_file, s=content)

    def fixed_headers(self, request, headers):
        if self.is_stealth and (request is None or self.is_route_special_request(request)):
            headers = copy.deepcopy(headers)
            headers['--add-script-inject--'] = 'true'
            return headers
        return headers

    def fix_body(self, body):
        if self.is_stealth:
            marker = ("//%s })();</script>" % self.uid).encode('utf-8')
            try:
                frag = Fragment(body, marker, sep=True)
                return frag[2]
            except IndexError:
                pass
        return body

    @staticmethod
    def is_route_special_request(request):
        return (
                request.resource_type == "document" and
                request.url.startswith("http") and
                request.method == 'GET' and
                quick_split_ct(request.headers.get('content-type', ''))[0] not in {
                    "application/x-www-form-urlencoded",
                    "multipart/form-data",
                }
        )

    async def context_route_all(self, context, default=None, hit=None, get_response=None):
        async def default_get_response(route):
            return await context.request.get(route.request.url, max_redirects=0)

        async def route_handler(route):
            if self.is_route_special_request(route.request):
                if get_response is None:
                    response = await default_get_response(route)
                else:
                    response = await get_response(route, context, default_get_response)
                if hit is not None:
                    await hit(route, response)
                if response is not None:
                    if isinstance(response, dict):
                        kwargs = response
                        kwargs['headers'] = self.fixed_headers(None, kwargs['headers'])
                    else:
                        kwargs = dict(response=response)
                        kwargs['headers'] = self.fixed_headers(None, response.headers)
                    await route.fulfill(**kwargs)
            else:
                if default is None:
                    await route.continue_()
                else:
                    await default(route)

        if self.is_stealth:
            context._impl_obj.route_injecting = True
            await context.route("**/*", route_handler)
        else:
            if default is not None:
                await context.route("**/*", default)
