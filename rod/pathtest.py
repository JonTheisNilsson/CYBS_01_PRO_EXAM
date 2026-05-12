import pathlib
from pathlib import Path
import os

print(pathlib.Path.cwd())
print(Path(__file__).resolve().parent)
print(os.path.realpath(__file__))
print(os.path.realpath(os.path.dirname(__file__)))

with open ('path.txt', 'w') as file:
    file.write('test')

#pathlib.Path.cwd().joinpath("test.txt")