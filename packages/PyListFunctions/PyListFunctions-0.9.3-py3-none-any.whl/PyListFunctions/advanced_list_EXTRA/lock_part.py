from typing import List, Union
from .type_part import type_part
__all__ = ['lock_part']


class lock_part(type_part):

    def _lock_check(self, __index: int):
        # 此时_i表示的是比第n个锁住的元素下标大
        _i = 0
        while __index > self._lock_lst[_i]:
            _i += 1
        for _i2 in range(_i, len(self._lock_lst)):
            self._lock_lst[_i2] -= 1

    def _lock_check2(self):
        self._lock_lst = list(map(lambda x: x - 1, self._lock_lst))

    def lock(self, __index: Union[int, List[int]] = None, writable: bool = True) -> None:
        self.writable = bool(writable)

        if __index is None:
            self._lock_all = True
        else:
            if not isinstance(__index, int) and not isinstance(__index, list):
                if self.ignore_error:
                    if not self.no_prompt:
                        print(f"Parameters cannot be {type(__index)}")
                else:
                    raise TypeError(f"Parameters cannot be {type(__index)}")

        if isinstance(__index, int):
            if __index > len(self) - 1 or __index < -len(self) + 1:
                if self.ignore_error:
                    print("list index out of range")
                else:
                    raise IndexError("list index out of range")
            else:
                self._lock_lst.append(__index)
        else:
            _tmp_lst = [item for item in __index if isinstance(item, int)]
            for i in range(len(_tmp_lst)):
                self.lock(_tmp_lst[i])

        if len(self._lock_lst) == len(self):
            self._lock_all = True
        return

    class LockError(Exception):
        def __init__(self, message):
            super().__init__(message)

    def view_lock_list(self) -> list:
        return self._lock_lst.copy()

    def unlock(self, __index: Union[int, List[int]] = None, writable: bool = True) -> None:
        self.writable = bool(writable)

        if __index is None:
            self._lock_lst.clear()
            self._lock_all = False
        else:
            if not isinstance(__index, int) and not isinstance(__index, list):
                if self.ignore_error:
                    if not self.no_prompt:
                        print(f"Parameters cannot be {type(__index)}")
                else:
                    raise TypeError(f"Parameters cannot be {type(__index)}")

            if len(self._lock_lst) <= len(self):
                self._lock_all = False

        if isinstance(__index, int):
            if __index not in self._lock_lst:
                if __index > len(self) - 1 or __index < -len(self) + 1:
                    if self.ignore_error:
                        print("list index out of range")
                    else:
                        raise IndexError("list index out of range")
                if self.ignore_error:
                    if not self.no_prompt:
                        print("This elements is not lock!")
                else:
                    raise ValueError("This elements is not lock!")
            else:
                self._lock_lst.remove(__index)
        else:
            _tmp_lst = [item for item in __index if isinstance(item, int)]
            for i in range(len(_tmp_lst)):
                self.unlock(_tmp_lst[i])
