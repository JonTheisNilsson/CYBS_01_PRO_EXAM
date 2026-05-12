def a():
    print(x)


def b():
    global x
    x=5
    a()

b()