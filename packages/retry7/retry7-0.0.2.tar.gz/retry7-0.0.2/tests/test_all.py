# from retry7 import retry
import retry7

retry = retry7.retry


def test_base():
    @retry()
    def f(x):
        return x - 1

    assert f(3) == 2


def test_exceptions_base():
    # catches generic exceptions
    tries = 0
    errored = None
    try:

        @retry(tries=2)
        def f():
            nonlocal tries
            tries += 1
            42 / 0

        f()
    except Exception as e:
        errored = e
    assert tries == 2
    assert isinstance(errored, ZeroDivisionError)


def test_exceptions_list_and_custom():
    class X1(Exception):
        pass

    class X2(Exception):
        pass

    thrown = []

    try:
        to_throw = 0

        @retry(exceptions=(X1, X2))
        def f():
            nonlocal to_throw
            if to_throw == 0:
                to_throw += 1
                raise X1()
            elif to_throw == 1:
                to_throw += 1
                raise X2()
            else:
                raise Exception()

        f()
    except Exception as e:
        thrown += [e]

    assert len(thrown) == 1
    assert not (isinstance(thrown[0], X1) or isinstance(thrown[0], X2))


def test_delay():
    slept = []

    def mock_sleep(x):
        nonlocal slept
        slept += [x]

    retry7.sleep = mock_sleep

    try:

        @retry(tries=3, delay=5)
        def f():
            raise Exception

        f()
    except Exception:
        pass

    assert len(slept) == 2
    assert slept[0] == 5
    assert slept[1] == 5


def test_backoff():
    slept = []

    def mock_sleep(x):
        nonlocal slept
        slept += [x]

    retry7.sleep = mock_sleep

    try:

        @retry(tries=3, delay=5, backoff=2)
        def f():
            raise Exception

        f()
    except Exception:
        pass

    assert len(slept) == 2
    assert slept[0] == 5
    assert slept[1] == 10


def test_class():
    class A:
        @retry(tries=3)
        def do_something(self, x):
            return x - 1

    assert A().do_something(5) == 4
