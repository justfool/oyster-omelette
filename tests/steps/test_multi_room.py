"""一次蓋多間房。步驟在 conftest.py。"""

from pytest_bdd import scenarios

scenarios("multi_room.feature")
