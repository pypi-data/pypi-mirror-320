# https://github.com/Kaliiiiiiiiii-Vinyzu/patchright-python/issues/9
import random
import string
import copy
from ..str import Fragment
from ..web.headers import quick_split_ct, quick_join_ct


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
    def fixed_headers(request, headers):
        # crNetworkManager.js
        # header.name === 'content-type' && header.value.includes('text/html'));
        if request.resource_type != 'document':
            ct = headers.get('content-type', '')
            if ct:
                k, p = quick_split_ct(ct)
                if k == 'text/html':
                    headers = copy.deepcopy(headers)
                    headers['content-type'] = quick_join_ct('text/plain', p)
                    return headers
        return headers

    @staticmethod
    def is_route_special_request(request):
        return request.resource_type == "document" and request.url.startswith("http")

    async def context_route_all(self, context, default, hit, get_response=None):
        async def default_get_response(route):
            return await context.request.get(route.request.url, max_redirects=0)

        async def route_handler(route):
            if self.is_route_special_request(route.request):
                if get_response is None:
                    response = await default_get_response(route)
                else:
                    response = await get_response(route, context, default_get_response)
                await hit(route, response)
                if response is not None:
                    if isinstance(response, dict):
                        kwargs = response
                    else:
                        kwargs = dict(response=response)
                    await route.fulfill(**kwargs)
            else:
                await default(route)

        if self.is_stealth:
            context._impl_obj.route_injecting = True
            await context.route("**/*", route_handler)
        else:
            await context.route("**/*", default)
