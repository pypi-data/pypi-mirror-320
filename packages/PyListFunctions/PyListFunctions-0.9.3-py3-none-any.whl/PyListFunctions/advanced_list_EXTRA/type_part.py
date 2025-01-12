from typing import Any, Union
from .initialization import __init__of_advanced_list
__all__ = ['type_part']


class type_part(__init__of_advanced_list):
    @staticmethod
    def __get_type_lst(lst: list) -> list:
        """
        Get the types of elements in this list
        :param lst:
        :return:
        """
        if not isinstance(lst, list):
            return [type(lst)]

        result_lst: list = []

        if len(lst) == 0:
            return [Any]

        for _i in range(len(lst)):
            if type(lst[_i]) is type:
                result_lst.append(lst[_i])
            else:
                result_lst.append(type(lst[_i]))
        return list(set(result_lst))

    def _type_check(self) -> None:
        i2 = 0
        try:
            for i in range(0, len(self)):
                if type(self[i2]) not in self.type_lst:
                    self.remove(self[i2])
                    i2 -= 1
                i2 += 1
        except IndexError:
            pass

    def type(self, _t: Union[list, Any] = None):
        if not self.use_type:
            self.type_lst = [Any]
            return
        if _t is None:
            _t = self
        self.type_lst = self.__get_type_lst(_t)

        self._type_check()

    def __setattr__(self, key, value):
        if key == 'use_type':
            self.type_lst = self.__get_type_lst(self)
            self._type_check()
        super().__setattr__(key, value)
