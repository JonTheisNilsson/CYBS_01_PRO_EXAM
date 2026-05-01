import pathlib
import os

print(pathlib.Path.cwd())
print(os.path.realpath(__file__))
print(os.path.realpath(os.path.dirname(__file__)))

with open ('path.txt', 'w') as file:
    file.write('test')