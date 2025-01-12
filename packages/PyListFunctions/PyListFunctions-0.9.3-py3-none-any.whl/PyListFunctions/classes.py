# -*- coding:utf-8 -*-

"""
 - The classes of list
"""

import typing as _typing

from .advanced_list_MAIN.reservation_part import reservation_part
from .limit_len_list import __limit_len_list__
from .SCRAPPED_type_list_class import __type_list__

Number = _typing.TypeVar("Number", int, float)
Module = _typing.NewType("Module", type(_typing))
Function = _typing.NewType("Function", lambda: None)


class advanced_list(reservation_part):
    def copy(self) -> 'advanced_list':
        """
        Return a shallow copy of the advanced_list.
        :return:
        """
        _copy_self = super().copy()
        _copy_self = advanced_list(_copy_self,
                                   use_type=self.use_type, type=self.type_lst,
                                   ignore_error=self.ignore_error,
                                   no_prompt=self.no_prompt,
                                   writable=self.writable,
                                   lock_all=self._lock_all, reservation=self.reservation,
                                   reservation_dict=self._reservation_dic)
        _tmp_lock_lst = self.view_lock_list()
        if not self._lock_all:
            for _i in range(len(_tmp_lock_lst)):
                self._copy_self.lock(_tmp_lock_lst.__getitem__(_i))

        _tmp_reservation_dic = self.view_reservation_dict()
        for key, value in _tmp_reservation_dic.items():
            self._copy_self.modifyReservationElement(key, value)

        return self._copy_self

    def __getitem__(self, item):
        if isinstance(item, slice):
            _slice_lst = []
            start = item.start if item.start is not None else 0
            stop = item.stop if item.stop is not None else len(self)
            step = item.step if item.step is not None else 1
            for _i in range(start, stop, step):
                self._slice_lst.append(super().__getitem__(_i))
            self._slice_lst = advanced_list(_slice_lst,
                                            use_type=self.use_type, type=self.type_lst,
                                            ignore_error=self.ignore_error,
                                            no_prompt=self.no_prompt,
                                            writable=self.writable,
                                            lock_all=self._lock_all)
            _tmp_lock_lst = self._lock_lst.copy()
            if not _tmp_lock_lst:
                return advanced_list(self._slice_lst)
            for _i2 in range(len(_tmp_lock_lst)):
                _tmp_lock_lst[_i2] -= start
            _tmp_lock_lst = [num for num in _tmp_lock_lst if num >= 0]
            _slice_lst.unlock()
            for _i in range(len(_tmp_lock_lst)):
                _slice_lst.lock(_tmp_lock_lst[_i])

            return _slice_lst

        else:
            return super().__getitem__(item)


class limit_len_list(__limit_len_list__):

    def __getitem__(self, item):
        if isinstance(item, slice):
            slice_lst = __limit_len_list__(self.__getitem__(
                slice(item.start if item.start is not None else 0, item.stop if item.stop is not None else len(self),
                      item.step if item.step is not None else 1)))
            slice_lst._MAX_len = self._MAX_len
            slice_lst.ignore_error = self.ignore_error
            slice_lst.no_prompt = self.no_prompt
            slice_lst.extend_retain = self.extend_retain
            return slice_lst.copy()
        else:
            return super().__getitem__(item)

    def only_copy_list(self):
        return super().copy()

    def copy(self) -> 'limit_len_list':
        copy_lst = super().copy()
        copy_lst = limit_len_list(copy_lst)
        copy_lst.setMAXlength(self._MAX_len)
        copy_lst.ignore_error, copy_lst.no_prompt, copy_lst.extend_retain = self.ignore_error, self.no_prompt, self.extend_retain
        return copy_lst


class type_list(__type_list__):
    """
     - THIS CLASS IS **SCRAPPED**!!!!!!!!!!

    This class inherits all the features of list !\n
    args: The value you want to assign a value to a list

    kwargs: REMEMBER Just only four parameters named 'type', 'retain(bool)', 'ignore_error(bool)' and 'no_prompt(bool)'

    type [type1, type2..., typeN]

    ignore_error (bool)

    no_prompt (bool)

    retain (bool)
    """
    pass
