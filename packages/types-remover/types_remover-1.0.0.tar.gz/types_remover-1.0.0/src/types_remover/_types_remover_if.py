import re


def _parse_line(line: str) -> str | bool:
    if '\n' in line:
        line = ''.join(line.split('\n'))
    spaces = len(line) - len(line.lstrip())
    variable_name = line[0:line.lstrip().index(' ') + len(line) - len(line.lstrip())].rstrip(':')
    lst = ''.join(line.split()).split('=')
    value = lst[1] if len(lst) == 2 else None
    if value is not None:
        return f'{' ' * spaces}{variable_name} = {value}'  # type: ignore
    return False


def _parse_def_statement(line: str) -> str:
    args2: list[str] = []
    spaces: int = len(line) - len(line.lstrip())
    raw_args: list[tuple[str, ...]] = re.findall(r'\b([a-zA-Z0-9_*]+):\s\w+|[,(]\s*([a-zA-Z0-9_*]+)\s*[,=]|,\s*([a-zA-Z0-9_*]+)\)', line)
    args = []
    try:
        for i in range(len(raw_args)):
            for j in range(len(raw_args[0])):
                if raw_args[i][j] != '':
                    args.append(raw_args[i][j].rstrip(','))
    except IndexError:
        args = ['']
    arg_values: list[str | None] = re.findall(r'=\s*([a-zA-Z0-9\'\".]+|\(\)|\[]|\{})', line)
    function_name: str = line[line.index('def') + 4:line.index('(')].strip()
    for i in range((len(args) - len(arg_values)) if '*' not in args else (len(args) - len(arg_values) - 1)):
        arg_values.insert(0, None)
    if '*' in args:
        arg_values.insert(-(len(args) - args.index('*') - 1), None)
    for i in range(len(args)):
        args2.append(' = '.join([args[i], arg_values[i]]) if arg_values[i] is not None else args[i])  # type: ignore
    return f'{' ' * spaces}def {function_name}({', '.join(args2)}):'


def remove_types(path: str, *, return_str: bool = False, output_file: str = 'output.py') -> None | str:
    with open(path) as f:
        file = [line.rstrip('\n') for line in f.readlines()]

    dict_deep: int = 0
    list_deep: int = 0
    tuple_deep: int = 0

    new_file: list[str] = []
    dict_line: str = ''
    list_line: str = ''
    tuple_line: str = ''
    tuple_is_func: bool = False

    for line in file:
        if 'import' in line:
            new_file.append(line)
            continue
        if (dict_deep + list_deep + tuple_deep) < 0:
            dict_deep, list_deep, tuple_deep = 0, 0, 0
        if (line.count('{') - line.count(repr('{'))) > (line.count('}') - line.count(repr('}'))):
            dict_deep += 1
        if (line.count('[') - line.count(repr('['))) > (line.count(']') - line.count(repr(']'))):
            list_deep += 1
        if (line.count('(') - line.count(repr('('))) > (line.count(')') - line.count(repr(')'))):
            tuple_deep += 1

        try:
            if line.split()[0][0] == '#':
                new_file.append(line)
                continue
            match line.split()[0]:
                case 'def':
                    if tuple_deep == 0:
                        new_file.append(_parse_def_statement(line))
                    else:
                        tuple_line += line
                        tuple_is_func = True
                case 'if' | 'case' | 'return' | 'for':
                    new_file.append(line)
                case _ if line.count('=') == 1:
                    if (dict_deep + list_deep + tuple_deep) == 0:
                        if line[line.index('=') - 2:line.index('=') + 1] in ['**=', '//=', '>>=', '<<=']:
                            operator = line[line.index('=') - 2:line.index('=') + 1]
                        elif line[line.index('=') - 1:line.index('=') + 1] in ['+=', '-=', '*=', '/=', '&=', '|=', '^=', '~=']:
                            operator = line[line.index('=') - 1:line.index('=') + 1]
                        else:
                            operator = '='
                        variable_name = line[0:line.lstrip().index(' ') + len(line) - len(line.lstrip())].rstrip(':')
                        if variable_name[-1] == ',':
                            variable_name = line[0:line.lstrip().index('=') + len(line) - len(line.lstrip())].split(':')[0]
                        lst = line.split('=')
                        value = lst[1] if len(lst) == 2 else None
                        if value is not None:
                            new_file.append(f'{variable_name} {operator}{value}')
                    elif dict_deep > list_deep and dict_deep > tuple_deep:
                        dict_line += line
                    elif tuple_deep > list_deep and tuple_deep > dict_deep:
                        tuple_line += line
                    elif list_deep > dict_deep and list_deep > tuple_deep:
                        list_line += line
                case _:
                    if (dict_deep + list_deep + tuple_deep) == 0:
                        if line.count(':') == 1 and line.count('=') == 0 and line.count(' ') == 1:
                            continue
                        new_file.append(line)
                    elif dict_deep > list_deep and dict_deep > tuple_deep:
                        dict_line += line
                    elif tuple_deep > list_deep and tuple_deep > dict_deep:
                        tuple_line += line
                    elif list_deep > dict_deep and list_deep > tuple_deep:
                        list_line += line
                    elif (dict_deep + list_deep + tuple_deep) < 0:
                        dict_deep, list_deep, tuple_deep = 0, 0, 0
                        new_file.append(line)
        except IndexError:
            new_file.append(line)
        if line.count('{') < line.count('}'):
            dict_deep -= 1
            if dict_line != '' and dict_deep == 0:
                new_line = _parse_line(dict_line)
                if new_line: new_file.append(new_line)  # type: ignore
                else: new_file.append(' ' * (len(dict_line) - len(dict_line.lstrip())) + ''.join(dict_line.split()))
                dict_line = ''
        if line.count('[') < line.count(']'):
            list_deep -= 1
            if list_line != '' and list_deep == 0:
                new_line = _parse_line(list_line)
                if new_line: new_file.append(new_line)  # type: ignore
                else: new_file.append(' ' * (len(list_line) - len(list_line.lstrip())) + ''.join(list_line.split()))
                list_line = ''
        if line.count('(') < line.count(')'):
            tuple_deep -= 1
            if tuple_line != '' and tuple_deep == 0 and tuple_is_func:
                tuple_line = ''.join(tuple_line.split('\n'))
                new_file.append(_parse_def_statement(tuple_line))
                tuple_line = ''
                tuple_is_func = False
            elif tuple_line != '' and tuple_deep == 0:
                new_line = _parse_line(tuple_line)
                if new_line: new_file.append(new_line)  # type: ignore
                else: new_file.append(' ' * (len(tuple_line) - len(tuple_line.lstrip())) + ''.join(tuple_line.split()))
                tuple_line = ''

    if return_str:
        return '\n'.join(new_file)
    with open(output_file, 'w') as f:
        f.writelines('\n'.join(new_file))
    return None