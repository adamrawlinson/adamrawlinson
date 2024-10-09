"""A partial function that can be ised to return a date
from a files creation or modification time."""


from datetime import datetime
import functools


global CREATED_TIME
CREATED_TIME: str = functools.partial(
    lambda a: str(datetime.date(datetime.strptime(time.ctime(
        os.path.getctime(a)), '%a %b %d %H:%M:%S %Y'))),
)

global MODIFIED_TIME
MODIFIED_TIME: str = functools.partial(
    lambda a: str(datetime.date(datetime.strptime(time.ctime(
        os.path.getmtime(a)), '%a %b %d %H:%M:%S %Y'))),
)


# Use:
# >>> CREATED_TIME(path\\to\\file)
# >>> '2024-01-31'

