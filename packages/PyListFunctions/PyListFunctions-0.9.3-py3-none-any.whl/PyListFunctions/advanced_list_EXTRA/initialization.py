from typing import Any
__all__ = ['__init__of_advanced_list']


class __init__of_advanced_list(list):

    # The two functions is must use in initialization for type

    @staticmethod
    def __get_type_lst(lst: list) -> list:
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

    def __init__(self, *args, **kwargs):
        """
        This class is part of the advanced_list!
        """
        self._type_dic = {}
        self._lock_lst = []
        self._copy_self = None
        self._slice_lst = None
        self._result_lst = None
        self._scope_of_impact = None
        self._scope_of_impact_element = None
        self.type_lst = []
        self.reservation = bool(kwargs.get("reservation"))
        if kwargs.get("reservation_dict"):
            self._reservation_dic = dict(kwargs.get("reservation_dict"))
        else:
            self._reservation_dic = {}
        self._lock_all = bool(kwargs.get("_lock_all"))
        if not bool(kwargs.get("writable")):
            self.writable = True
        else:
            self.writable = bool(kwargs.get("writable"))
        self.use_type: bool = bool(kwargs.get("use_type"))
        self.ignore_error: bool = bool(kwargs.get("ignore_error"))
        self.no_prompt: bool = bool(kwargs.get("no_prompt"))
        self._t = kwargs.get("type")
        self._None_t = False
        self._B_T_arg = False

        if args != () and len(args) == 1 and isinstance(list(args)[0], list):
            super().__init__(list(args)[0])
            self._B_T_arg = True
            self._T_arg = list(args)[0]
        else:
            super().__init__(args)

        if not self.use_type:
            self.type_lst = [Any]
            return

        if self._t is None:
            self._None_t = True
        if isinstance(self._t, list):
            if len(self._t) > 0:
                for _i in range(len(self._t)):
                    if not (type(self._t[_i]) is type):
                        self._type_dic[_i] = type(self._t[_i])
                    else:
                        self._type_dic[_i] = self._t[_i]
            else:
                self._type_dic[0] = Any
        else:
            if self._B_T_arg:
                self.type_lst = self.__get_type_lst(self._T_arg)
            else:
                self.type_lst = self.__get_type_lst(list(args))
        if not self._None_t:
            for _i in range(len(self._type_dic)):
                self.type_lst.append(self._type_dic[_i])

        self._type_check()
