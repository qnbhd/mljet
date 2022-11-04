# import inspect
# import re
#
# pyfunc_with_body = re.compile(r"(?P<indent>[ \t]*)(async def|def)[ \t]*(?P<name>\w+)\s*\((?P<params>.*?)\)(?:[ "
#                               r"\t]*->[ \t]*(?P<return>\w+))?:(?P<body>(?:\n(?P=indent)(?:[ \t]+[^\n]*)|\n)+)")
#
# text = '''
# def main():
#     with open('a/b/c/file.txt', 'w') as f:
#         f.write('hello!')
#
# # hhh
#
# async def ww(a: int, b: float, c: real) -> str:
#     # abcdedf
#     with open('a/b/c/file.txt', 'w') as f:
#         # wow
#         f.write('hello!')
#         # oh my god
#     # hhh
# '''
#
#
# def replace_functions_by_names(source, names2repls):
#     """Replace functions by names in source code with `repl_codes`."""
#     new_source = source
#     replaced = []
#     for m in pyfunc_with_body.finditer(source):
#         source_with_signature = m.group(0)
#         name = m.group('name')
#         if name not in names2repls:
#             continue
#         argspec = m.group('params')
#         argscount = len(argspec.split(','))
#         if argscount != len(inspect.getfullargspec(names2repls[name]).args):
#             raise TypeError(f"Method `{name}` takes {argscount} arguments, but "
#                             f"{len(inspect.getfullargspec(names2repls[name]).args)} were given")
#         repl_code = inspect.getsource(names2repls[name])
#         new_source = new_source.replace(source_with_signature, repl_code)
#         replaced.append(name)
#
#     if len(replaced) != len(names2repls):
#         raise ValueError(f"Replaced {len(replaced)} functions, but {len(names2repls)} were given")
#
#     return new_source
#
#
# def ww(a: int, b: float, c) -> str:
#     pass
#
#
# source = replace_functions_by_names(text, {'ww': ww})
#
#
# print(source)
