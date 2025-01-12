from typing import Any, Literal, Hashable
from re import findall, split
from os import system

DigitKey = Literal['digit_key']
StrKey = Literal['string_key']
Keyable = DigitKey| StrKey
Indexable = Literal['indexable']
Sliceable = Literal['sliceable']
Accessable = Keyable| Indexable| Sliceable

DictionaryType = Literal['dictionary_type']
Assignable = DictionaryType

SequenceType = Literal['sequence_type']
Unassignable = SequenceType

ReturnValueType = Assignable| Unassignable


class Diction:

    def __init__(self, data: dict=None):
        self.__cut_paths_pattern: str  = r'(?<!\\)\.'
        self.__sliceable_pattern: str = r'@(?:([\d-]*):([\d-]*):?([\d-]*):?|([\d-]+))$'
        self.__escapetor: str = '\\'
        self.__escapetors: str = '\\.@:#'
        self.__data: dict = data if data is not None else {}
        self.__expand: dict = {}
        pass

    def __repr__(self):
        return self.__data.__repr__()

    def __getitem__(self, access_paths: str) -> Any:
        return self.__iter_item(self.__cut_paths(access_paths))
            
    def __setitem__(self, access_paths: str| Hashable, value: Any):
        if not isinstance(access_paths, str) or access_paths == '':
            self.__data[access_paths] = value
            return

        *accessors, accessor = self.__cut_paths(access_paths)
        target = self.__iter_item(accessors) if len(accessors) != 0 else self.__data
        error: Exception = Exception('this diction is unassignable')

        accessor, error = self.__convert_accessor(accessor)

        try:
            target[accessor] = value
        except:
            raise error
        return

    def __cut_paths(self, access_paths: str) -> list[str]:
        return split(self.__cut_paths_pattern, access_paths)

    def __iter_item(self, accessors: list[str]) -> dict| list| Any:
        result: dict| Any = self.__data
        error: Exception = None

        for accessor in accessors:
            accessor, error = self.__convert_accessor(accessor)

            try:
                result = result[accessor]
            except:
                raise error
        return result

    def __convert_accessor(self, accessor: str) -> list[str| int| slice, Exception]:
        match self.__accessor_type(accessor):
            case 'digit_key':
                return [
                    self.__digit_key_get(accessor), 
                    Exception(f'{accessor[1:]} not in this diction')
                ]

            case 'string_key':
                return [
                    self.__string_key_get(accessor),
                    Exception(f'{accessor[1:]} not in this diction')
                ]

            case 'indexable':
                return [
                    self.__index_key_get(accessor), 
                    Exception(f'index `{accessor[1:]}` out of range')
                ]

            case 'sliceable':
                return [
                    self.__slice_gets(accessor), 
                    Exception(f'slice not suport assignment')
                ]

    def __accessor_type(self, accessor: str) -> Accessable:
        groups = findall(self.__sliceable_pattern, accessor)

        if groups == []:
            if accessor == '':
                return 'string_key'
            elif accessor[0] == '#':
                return 'digit_key'
            return 'string_key'
        
        if groups[0][3] != '':
            return 'indexable'
        
        return 'sliceable'

    def __string_key_get(self, string_key: str) -> str:
        result: str = ''
        last_character: str = ''

        for character in string_key:
            result += character if \
                character not in self.__escapetor \
                or (last_character == self.__escapetor and character in self.__escapetors) \
                else ''
            
            last_character = character if \
                last_character != self.__escapetor \
                or character not in self.__escapetors \
                else ''
        
        return result

    def __digit_key_get(self, digit: str) -> int| float:
        return int(digit[1:])

    def __index_key_get(self, index: str) -> int:
        *_, index = findall(self.__sliceable_pattern, index)[0]
        return index

    def __slice_gets(self, slicer: str) -> slice:
        start, stop, step, _= findall(self.__sliceable_pattern, slicer)[0]
        return slice(
            int(start) if start != '' else None,
            int(stop) if stop != '' else None,
            int(step) if step != '' else None,
        )

       


def main_entrance():
    system('cls')   
    d: dict = {}
    d[''] = 0
    d['.'] = 1
    d['@'] = 2
    d['@:'] = 3
    d['@::'] = 4
    d['']
    print(d)
    # 字典路径
    d: Diction = Diction({})
    d[''] = 0
    d['\.'] = 1
    d['\@'] = 2
    d['\@\:'] = 3
    d['\@\:\:'] = 4
    print(d)
    pass


def test():
    # a = lambda: Keyable
    # print(a())
    # print(Literal('keyable'))
    # print(Literal('keyable') == a())
    pass


if __name__ == '__main__':
    main_entrance()
    # test()
    pass
