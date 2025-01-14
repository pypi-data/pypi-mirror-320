from random import uniform
from time import sleep


def retry(
    exceptions=Exception,
    tries=-1,
    delay=0,
    max_delay=None,
    backoff=1,
    jitter=0,
    logger=None,
):
    def decorator(f):
        def do_it(*args, **kwargs):
            _tries, _delay = tries, delay
            while _tries:
                try:
                    return f(*args, **kwargs)
                except exceptions as e:
                    _tries -= 1
                    if _tries == 0:
                        raise e

                    if logger is not None:
                        logger.warning(f"{e}, retrying in {delay} seconds...")

                    sleep(_delay)
                    _delay *= backoff

                    if isinstance(jitter, tuple):
                        _delay += uniform(*jitter)
                    else:
                        _delay += jitter

                    if max_delay is not None:
                        _delay = min(_delay, max_delay)

        return do_it

    return decorator
