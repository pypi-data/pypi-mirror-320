from typing import Any, Optional, Union
from .lock_part import lock_part
__all__ = ['other_func_part']


class other_func_part(lock_part):

    def replace(self, __o_obj: Any = None, __n_obj: Any = None, *, start: int = 0, end: int = None, step: int = 1, None_mode_original: bool = False, None_mode_new_value: bool = False) -> None:

        if self._lock_all:
            if self.ignore_error:
                if not self.no_prompt:
                    print("All elements is locked, The replace function cannot be called")
            else:
                raise self.LockError("All elements is locked, The replace function cannot be called")

        if step < 1:
            raise ValueError("step cannot less than 1")

        if end is None:
            end = len(self)
        elif not isinstance(end, int) or end > len(self):
            end = len(self)

        if start > end:
            raise ValueError("start cannot more than end")
        self._scope_of_impact = []
        try:
            if __o_obj is None and not None_mode_original:
                for _i in range(start, end, step):
                    if __n_obj is None:
                        if None_mode_new_value:
                            super().__setitem__(_i, None)
                        else:
                            if _i not in self._lock_lst:
                                self._scope_of_impact.append(_i)
                            else:
                                super().__setitem__(_i, None)
                    else:
                        if _i not in self._lock_lst:
                            super().__setitem__(_i, __n_obj)
            else:
                for _i in range(start, end, step):
                    if super().__getitem__(_i) is __o_obj:
                        if __n_obj is None:
                            if None_mode_new_value:
                                super().__setitem__(_i, None)
                            else:
                                if _i not in self._lock_lst:
                                    self._scope_of_impact.append(_i)
                        else:
                            if _i not in self._lock_lst:
                                super().__setitem__(_i, __n_obj)
            if __n_obj is None and len(self._scope_of_impact) != 0:
                self._scope_of_impact = list(reversed(self._scope_of_impact))
                for _i in range(len(self._scope_of_impact)):
                    super().pop(self._scope_of_impact[_i])
                self._scope_of_impact = list(reversed(self._scope_of_impact))
            if len(self._scope_of_impact) != 0 and len(self._lock_lst) != 0:
                _i = 0
                while self._scope_of_impact[0] > self._lock_lst.__getitem__(_i):
                    _i += 1
                _i3 = 1
                for _i2 in range(_i, len(self._lock_lst)):
                    self._lock_lst[_i2] -= _i3
                    _i3 += 1
        except IndexError:
            pass

    def index_pro(self, item: Any, start: int = 0, end: int = None, first: bool = False) -> Union[int, tuple]:
        if end is None:
            end = len(self)
        self._result_lst = []

        for _i in range(start, end, 1):
            if super().__getitem__(_i) is item:
                if first:
                    return _i
                self._result_lst.append(_i)

        if len(self._result_lst) != 0:
            return tuple(self._result_lst)
        else:
            raise ValueError(f"{item} is not in advanced_list")

    def only_copy_list(self) -> list:
        return super().copy()

    def end(self) -> Optional[int]:
        _tmp_iter = iter(self)
        _i = -1
        try:
            while True:
                next(_tmp_iter)
                _i += 1
        except StopIteration:
            if _i == -1:
                return None
            else:
                return _i

    def exchange(self, subscript1: int, subscript2: int) -> None:
        _temp = super().__getitem__(subscript1)
        super().__setitem__(subscript1, super().__getitem__(subscript2))
        super().__setitem__(subscript2, _temp)
