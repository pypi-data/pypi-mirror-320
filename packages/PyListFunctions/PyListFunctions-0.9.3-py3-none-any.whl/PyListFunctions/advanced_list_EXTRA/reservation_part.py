from .other_func_part import other_func_part
__all__ = ['reservation_part']


class reservation_part(other_func_part):
    _reservation_dic = {}
    normal_print: bool = False

    def __setitem__(self, key, value):
        if key > len(self)-1:
            if self.reservation:
                self._reservation_dic.update({key: value})
                if not self.no_prompt:
                    print("value has been saved")
            else:
                super().__setitem__(key, value)

    def modifyReservationElement(self, *args) -> None:
        if len(args) == 1:
            args = list(args)
            if not isinstance(args[0], dict):
                if self.ignore_error:
                    if not self.no_prompt:
                        print(f"invalid type of parameter: {type(args[0])}")
                        return
                else:
                    raise TypeError(f"invalid type of parameter: {type(args[0])}")

            re_dic = {k: v for k, v in args[0].copy().items() if isinstance(k, int)}

            if not re_dic:
                if self.ignore_error:
                    if not self.no_prompt:
                        print(f"invalid type of key")
                        return
                else:
                    raise TypeError(f"invalid type of key")

            for key, value in re_dic.items():
                self.modifyReservationElement(key, value)

        elif len(args) == 2:
            args = list(args)
            if not isinstance(args[0], int):
                if self.ignore_error:
                    if not self.no_prompt:
                        print(f"invalid type of parameter: {type(args[0])}")
                else:
                    raise TypeError(f"invalid type of parameter: {type(args[0])}")

            if args[0] < len(self) - 1:
                if self.ignore_error:
                    if not self.no_prompt:
                        print("Reservation element create failed!")
                        return
                else:
                    raise ValueError("Reservation element create failed!")
            if args[0] in list(self._reservation_dic.keys()):
                if not self.no_prompt:
                    print("Reservation element subscript has been changed!")
            self._reservation_dic.update({args[0]: args[1]})

        else:
            if self.ignore_error:
                if not self.no_prompt:
                    print(f"modifyReservationElement() takes 1 or 2 positional arguments but {len(args)} was given")
            else:
                raise TypeError(f"modifyReservationElement() takes 1 or 2 positional arguments but {len(args)} was given")

    def delReservationElement(self, _subscript: int) -> None:
        if _subscript not in list(self._reservation_dic.keys()):
            if self.ignore_error:
                if not self.no_prompt:
                    print("Reservation element delete failed!")
                    return
            else:
                raise ValueError("Reservation element delete failed!")
        self._reservation_dic.pop(_subscript)

    def clearReservationElement(self) -> None:
        self._reservation_dic.clear()

    def view_reservation_dict(self) -> dict:
        return self._reservation_dic.copy()
