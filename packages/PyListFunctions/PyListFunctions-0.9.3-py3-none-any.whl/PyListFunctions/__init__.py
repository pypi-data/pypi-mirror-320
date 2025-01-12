# -*- coding:utf-8 -*-

"""
 - **Author: BL_30G** (https://space.bilibili.com/1654383134)
 - **Version: 0.9.3**
 - **Installation requirements: No dependencies packages** (csv_to_lst_or_dic() function depends on pandas package)
 - **Python Version：3.7 and above**
"""


# list func area


def get_type_lst(lst):
    """
    Get the types of elements in this list

    Example:

    >>> get_type_lst([])
    [Any]
    >>> get_type_lst([object])
    [Any]
    >>> get_type_lst([1, 1.45])
    [int, float]
    >>> get_type_lst("string")
    [str]
    >>> get_type_lst([1.14, int])
    [float, int]

    :param lst:
    :return:
    """
    pass


def tidy_up_list(lst, bool_mode=False, eval_mode=False, float_mode=False, int_mode=False, none_mode=False):
    """
    - Nearly SCRAPPED

    A function to tidy up list

    :param float_mode:
    :param int_mode:
    :param none_mode:
    :param bool_mode: If you want to turn such as 'True' into True which it is in this list, you can turn on 'bool_mode'
    :param eval_mode: If you want to turn such as '[]' into [] which it is in this list, you can turn on 'eval_mode'
    :param lst:put list which you need to sorting and clean
    :return: the perfect list
    """
    pass


def deeply_tidy_up_list(lst):
    """
    This Function can search list elements and tidy up it too

    :param lst:put list which you need to sorting and clean
    :return: the perfect list
    """
    pass


def bubble_sort(lst, if_round=False, in_reverse_order=False):
    """
    - A simple bubble sort function

    :param lst: The list you need to sort
    :param if_round: Rounding floating-point numbers
    :param in_reverse_order: Reverse the list
    :return: The sorted list
    """
    pass


def list_calculation(*args, calculation="+", multi_calculation="", nesting=False):
    """
    The function for perform calculation on multiple lists

    Example:
    --------

    >>> lst_t1, lst_t2, lst_t3, lst_t4 = [4], [11, 45, 14, 1], [810, 3], [19, 19, 2]
    >>> lst_t_All = [lst_t1, lst_t2, lst_t3, lst_t4, [], []]
    >>> list_calculation(lst_t_All, calculation='+', nesting=True)
    [844, 67, 16, 1]
    >>> list_calculation(lst_t_All, calculation='+', multi_calculation="+,-", nesting=True)
    [-776, 61, 16, 1]

    operation:
    ------

    result1 -> [11+19+810+4, 45+19+3, 14+2, 1] = [844, 67, 16, 1]
    result2 -> [11+19-810+4, 45+19-3, 14+2, 1] = [-776, 61, 16, 1]


    :param args: The lists to calculation
    :param calculation: An calculation symbol used between all lists (Only one)(default:"+")(such as "+", "-", "*", "/", "//", "%")
    :param multi_calculation: Different calculation symbols between many lists (Use ',' for intervals.)
    :param nesting: If the lists you want to calculation are in a list, You should turn on 'nesting' to clean the nesting list
    :return: The result of lists
    """
    pass


def var_in_list(lst, __class, return_lst=False, only_return_lst=False):
    """
    Returns the number of variables in the list that match the type given by the user

    Example
    ------

    >>> lst = list(range(9))
    >>> var_in_list(lst, int)
    9
    >>> var_in_list(lst, int, return_lst=True)
    (9, [0, 1, 2, 3, 4, 5, 6, 7, 8])
    >>> var_in_list(lst, int, only_return_lst=True)
    [0, 1, 2, 3, 4, 5, 6, 7, 8]

    :param lst: The list
    :param __class: The class of variable you want to find
    :param return_lst: Returns a list of variables that match the type
    :param only_return_lst: Only returns a list of variables that match the type
    :return:
    """
    pass


def in_list_calculation(lst, calculation="+", multi_calculation=""):
    """
    - A function to calculation all the int or float in the list
    :param lst:
    :param calculation: A calculation symbol used between all lists (Only one)(default:"+")(such as "+", "-", "*", "/", "//", "%")
    :param multi_calculation: Different calculation symbols between many lists (Use ',' for intervals)
    :return:
    """
    pass


def csv_to_lst_or_dic(csv, dict_mode=False):
    """
    - Can turn csv you read into list or dict
    :param csv:
    :param dict_mode: turn csv you read into dict
    :return:
    """
    pass


def len_sorted_lst(lst, reverse=False, filtration=True):
    """
    - This function according to the len of list to sort the lists(From small to large)
    :param lst:
    :param reverse: If is true the order will reverse
    :param filtration: If is true it will clear the type of variable isn't list(these variable will append at the lists right)
    :return:
    """
    pass


def populate_lsts(*args, _type: object = 1, nesting=False):
    """
    - This function will populate the list with less than the longest list length according to the length of the list until the longest list length is met

    Example:
    --------

    >>> lst1, lst2, lst3 = [0, 1, 2], [3, 4], [5, 6, 7, 8]
    >>> populate_lsts(lst1, lst2, lst3, _type="what you want to add")
    >>> lst1
    [0, 1, 2, "what you want to add"]
    >>> lst2
    [3, 4, "what you want to add"]
    >>> lst3
    [5, 6, 7, 8, "what you want to add"]


    :param _type: the thing you want to populate
    :param nesting: If the lists you want to populate are in a list, You should turn on 'nesting' to clean the nesting list
    :return:
    """
    pass


def remove_nesting(lst):
    """
    - An easy function to remove nesting of list

    Example:
    ---------

    >>> remove_nesting([0, [1, 2, [3, 4], 5], 6])
    [0, 1, 2, 3, 4, 5, 6]

    :param lst:
    :return:
    """
    pass


def list_internal_situation(lst):
    """
    - This function will print all variable in the list

    Example:
    ---------

    >>> list_internal_situation(['1', '2', 1, 2, ['a', ['false', 'True'], ['Ture', 5, 8, [10, 'False', 'True']]]])

    0 -> value: 1 <class 'str'>\n
    1 -> value: 2 <class 'str'>\n
    2 -> value: 1 <class 'int'>\n
    3 -> value: 2 <class 'int'>\n
    4 -> value: ['a', ['false', 'True'], ['Ture', 5, 8, [10, 'False', 'True']]] <class 'list'>\n
    in index(4) -> 0 -> value: a <class 'str'>\n
    in index(4) -> 1 -> value: ['false', 'True'] <class 'list'>\n
    in index(4) -> in index(1) -> 0 -> value: false <class 'str'>\n
    in index(4) -> in index(1) -> 1 -> value: True <class 'str'>\n
    in index(4) -> 2 -> value: ['Ture', 5, 8, [10, 'False', 'True']] <class 'list'>\n
    in index(4) -> in index(2) -> 0 -> value: Ture <class 'str'>\n
    in index(4) -> in index(2) -> 1 -> value: 5 <class 'int'>\n
    in index(4) -> in index(2) -> 2 -> value: 8 <class 'int'>\n
    in index(4) -> in index(2) -> 3 -> value: [10, 'False', 'True'] <class 'list'>\n
    in index(4) -> in index(2) -> in index(3) -> 0 -> value: 10 <class 'int'>\n
    in index(4) -> in index(2) -> in index(3) -> 1 -> value: False <class 'str'>\n
    in index(4) -> in index(2) -> in index(3) -> 2 -> value: True <class 'str'>\n

    :param lst:
    :return:
    """
    pass


def uniformly_slice_list(lst, num_parts):
    """
    - This function divides the list evenly into nested lists of nums by the num value given

    Example:
    ---------

    >>> uniformly_slice_list(list(range(1, 10)), 3)
    [[1, 2, 3], [4, 5, 6], [7, 8, 9]]

    :param lst:
    :param num_parts:
    :return:
    """
    pass


def slice_two_dimensional_list(lst):
    """
    - Merge each column of the 2D list into a new list, and then put it into a new list.

    Example:
    --------

    >>> result = slice_two_dimensional_list([[0, 1, 2], [3, 4, 5], [6, 7, 8]])
    >>> print(result)
    [[0, 3, 6], [1, 4, 7], [2, 5, 8]]

    :param lst:
    :return:
    """
    pass


def location_moving(lst: list, offset: int) -> list:
    """
    - Offset within the original list

    Example:
    --------

    >>> lst1 = [1, 2, 3, 4, 5]
    >>> print(location_moving(lst1, 1), location_moving(lst1, -1))
    [5, 1, 2, 3, 4] [2, 3, 4, 5, 1]

    :param lst:
    :param offset:
    :return:
    """
    pass


# str functions area

def replace_str(string, __c, __nc='', num=0, __start=0, __end=None):
    # This Function is Finished!
    """
    - Change the character in the string to a new character, but unlike "str.replace()", num specifies the number of original strs that that need to change (not the maximum times of changes)
    :param string: The string
    :param __c: Original character
    :param __nc: New character
    :param num: How many character(default is Zero(replace all Eligible character))
    :param __start:
    :param __end:
    :return:
    """
    pass


def randstr(length, *, use_symbol=False, without_character=False):
    """
    - Generate a string of random ASCII characters
    :param length:
    :param use_symbol:
    :param without_character:
    """
    pass


def reverse_str(string):
    """
    A very, very easy function to reverse str（混水分
    :param string: The string you want to reverse
    :return: the reversed str
    """
    pass


def statistics_str(string):
    """
    Return the statistics of the string,
    include the sort of the character according to ASCII Table and the appeared numbers of the character in this string
    :param string: The string you need statistics
    :return: The statistics of the string
    """
    pass


def find_list(lst, __fc, start=False, mid=False, end=False):
    """
    Based on the string given by the user, find the string that contains this string in the list.
    :param lst: The list you want to find
    :param __fc: The character in list in string
    :param start: Only find on list start
    :param mid: Only find on list middle
    :param end: Only find on list end
    :return: List of find result
    """
    pass


# other

def can_variable(string):
    """
    The function can judge the string can or cannot be variable
    :param string:
    :return:
    """
    import gc

    string = str(string)
    judgment_lst = ["False", "None", "True", "and", "as", "assert", "break", "case", "class", "continue", "def", "del",
                    "elif",
                    "else", "except", "finally", "for", "from", "global", "if", "import", "in", "is", "lambda",
                    "match", "nonlocal", "not", "or",
                    "pass", "raise", "return", "try", "while", "with", "yield"]
    C_variable: bool = True

    if string in judgment_lst:
        C_variable = False
    elif not string.isalpha():
        C_variable = False
    elif 48 <= ord(string[0:]) <= 57:
        C_variable = False

    del judgment_lst
    gc.collect()
    return C_variable


def nrange(*args: int):
    if len(args) == 1:
        i: int = 0
        for j in range(args[0]):
            i += 1
        return i
    elif len(args) == 2:
        i: int = 0
        for j in range(args[0], args[1]):
            i += 1
        return i
    else:
        if len(args) == 3:
            i: int = 0
            for j in range(args[0], args[1], args[2]):
                i += 1
            return i


def MustType(parameter):
    """
    This is a decorator to check the type of parameters for function

    - Usage 1: @MustType
    - Usage 2: @MustType(True) (If this is the case, the decorator will check to see if the type of the returned result matches the callout type)
    - Usage 3: @MustType(False) (equal to @MustType)

    Example:
    --------

    >>> @MustType
    ... def func1(para1, *args, para2=object(), **kwargs):
    ...     pass
    ...
    >>> @MustType(True)
    ... def func1(para1, *args, para2=object(), **kwargs):
    ...     pass
    ...
    >>>

    :param parameter:
    :return:
    """

    import inspect
    empty = inspect._empty

    if isinstance(parameter, bool):
        import inspect, functools

        def decorator(func):
            function_signature = inspect.signature(func)

            @functools.wraps(func)
            def wrapper(*args, **kwargs):

                # 将传入的参数绑定到函数签名上
                bound_args = function_signature.bind(*args, **kwargs)

                # 检查普通位置参数（POSITIONAL_OR_KEYWORD 和 POSITIONAL_ONLY 类型）的类型
                for name, param in function_signature.parameters.items():
                    if param.kind in (inspect.Parameter.POSITIONAL_OR_KEYWORD, inspect.Parameter.POSITIONAL_ONLY):
                        value = bound_args.arguments[name]
                        parameter_type = param.annotation
                        if parameter_type is not empty and not isinstance(value, parameter_type):
                            raise TypeError(f"The type of the parameter ({name}) should be {parameter_type}, but the {type(value)} type is actually passed")

                # 检查可变位置参数（VAR_POSITIONAL 类型，即 *args）的类型
                if "args" in function_signature.parameters and bound_args.arguments.get("args"):
                    args_param = function_signature.parameters["args"]
                    args_value = bound_args.arguments["args"]
                    args_type = args_param.annotation
                    for element in args_value:
                        if args_type is not empty and not isinstance(element, args_type):
                            raise TypeError(f"The element type in *args should be {args_type}, but there are elements that do not match the type")

                # 检查可变关键字参数（VAR_KEYWORD 类型，即 **kwargs）的类型
                if "kwargs" in function_signature.parameters and bound_args.arguments.get("kwargs"):
                    kwargs_param = function_signature.parameters["kwargs"]
                    kwargs_value = bound_args.arguments["kwargs"]
                    kwargs_type = kwargs_param.annotation
                    for key, value in kwargs_value.items():
                        if kwargs_type is not empty and not isinstance(value, kwargs_type):
                            raise TypeError(
                                f"The type of parameter {key} in **kwargs should be {kwargs_type}, but the actual {type(value)} is passed in")

                result = func(*args, **kwargs)
                if func.__annotations__['return'] is not None:
                    if not isinstance(type(result), type(func.__annotations__['return'])):
                        raise TypeError(f"A result of type {type(func.__annotations__['return'])} should be transmitted, but the actual result type is: {type(result)}")
                elif func.__annotations__['return'] is None:
                    if result is not None:
                        raise TypeError(f"A result of None should be transmitted, but the actual result type is: {type(result)}")
                return result

            return wrapper

        return decorator

    elif inspect.isfunction(parameter):
        import inspect
        import functools

        function_signature = inspect.signature(parameter)

        @functools.wraps(parameter)
        def wrapper(*args, **kwargs):

            # 将传入的参数绑定到函数签名上
            bound_args = function_signature.bind(*args, **kwargs)

            # 检查普通位置参数（POSITIONAL_OR_KEYWORD 和 POSITIONAL_ONLY 类型）的类型
            for name, param in function_signature.parameters.items():
                if param.kind in (inspect.Parameter.POSITIONAL_OR_KEYWORD, inspect.Parameter.POSITIONAL_ONLY):
                    value = bound_args.arguments[name]
                    parameter_type = param.annotation
                    if parameter_type is not empty and not isinstance(value, parameter_type):
                        raise TypeError(f"The type of the parameter ({name}) should be {parameter_type}, but the {type(value)} type is actually passed")

            # 检查可变位置参数（VAR_POSITIONAL 类型，即 *args）的类型
            if "args" in function_signature.parameters:
                args_param = function_signature.parameters["args"]
                args_value = bound_args.arguments["args"]
                args_type = args_param.annotation
                for element in args_value:
                    if args_type is not empty and not isinstance(element, args_type):
                        raise TypeError(f"The element type in *args should be {args_type}, but there are elements that do not match the type")

            # 检查可变关键字参数（VAR_KEYWORD 类型，即 **kwargs）的类型
            if "kwargs" in function_signature.parameters:
                kwargs_param = function_signature.parameters["kwargs"]
                kwargs_value = bound_args.arguments["kwargs"]
                kwargs_type = kwargs_param.annotation
                for key, value in kwargs_value.items():
                    if kwargs_type is not empty and not isinstance(value, kwargs_type):
                        raise TypeError(f"The type of parameter {key} in **kwargs should be {kwargs_type}, but the actual {type(value)} is passed in")

            result = parameter(*args, **kwargs)
            return result

        return wrapper


def Dynamic_Class_Copy(func):
    """
    This is a decorator that replaces the dynamic classes contained in the incoming parameters,
    which will be replaced with the copied results (including the nested dynamic classes)

    Example:
    --------

    >>> @Dynamic_Class_Copy
    ... def test_func(lst: list):
    ...     lst[0].append(1)
    ...     lst.append(1)
    >>> test_lst = [[]]
    >>> test_func(test_lst)
    >>> print(test_lst)
    [[]]

    :param func:
    :return:
    """

    from collections.abc import Mapping, Sequence, Set

    def recursion_copy(Obj):
        is_seq = False
        is_mapping = False
        is_set = False
        if isinstance(Obj, Sequence):
            is_seq = True
        elif isinstance(Obj, Mapping):
            is_mapping = True
        elif isinstance(Obj, Set):
            is_set = True
            if isinstance(Obj, frozenset):
                return frozenset(recursion_copy(item) for item in Obj)
            else:
                is_set = True

        if is_seq:
            new_seq = type(Obj)(list(recursion_copy(item) for item in Obj))
            return new_seq
        elif is_mapping:
            new_dict = type(Obj)({key: recursion_copy(value) for key, value in Obj.items()})
            return new_dict
        elif is_set:
            new_set = type(Obj)(recursion_copy(item) for item in Obj)
            return new_set
        return Obj

    def wrapper(*args, **kwargs):
        new_args = []
        for arg in args:
            new_args.append(recursion_copy(arg))

        new_kwargs = {}
        for key, value in kwargs.items():
            new_kwargs[key] = recursion_copy(value)

        return func(*new_args, **new_kwargs)

    return wrapper


import importlib
from .list_func_part import *
from .str_func_part import *

classes = importlib.import_module(".classes", package="PyListFunctions")
