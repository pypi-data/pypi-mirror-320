async def async_safe_process(
        func, default=None, closed=None, timeout=None, message=None, others=None, messages=None, stealth=True,
        args=None, kwargs=None):
    if stealth:
        from patchright._impl._errors import Error, is_target_closed_error, TimeoutError
    else:
        from playwright._impl._errors import Error, is_target_closed_error, TimeoutError
    try:
        args = [] if args is None else args
        kwargs = {} if kwargs is None else kwargs
        return await func(*args, **kwargs)
    except Error as e:
        if is_target_closed_error(e):
            if closed:
                return await closed(e)
        elif isinstance(e, TimeoutError):
            if timeout:
                return await timeout(e)
        elif messages and any(msg in e.message for msg in messages):
            if message:
                return await message(e)
        else:
            if others:
                return await others(e)
            else:
                raise e from None
    return default


async def async_none(e):
    pass


async def async_raise(e):
    raise e from None


def sync_safe_process(
        func, default=None, closed=None, timeout=None, message=None, others=None, messages=None, stealth=True,
        args=None, kwargs=None):
    if stealth:
        from patchright._impl._errors import Error, is_target_closed_error, TimeoutError
    else:
        from playwright._impl._errors import Error, is_target_closed_error, TimeoutError
    try:
        args = [] if args is None else args
        kwargs = {} if kwargs is None else kwargs
        return func(*args, **kwargs)
    except Error as e:
        if is_target_closed_error(e):
            if closed:
                return closed(e)
        elif isinstance(e, TimeoutError):
            if timeout:
                return timeout(e)
        elif messages and any(msg in e.message for msg in messages):
            if message:
                return message(e)
        elif others:
            return others(e)
    return default


def sync_none(e):
    pass


def sync_raise(e):
    raise e from None
