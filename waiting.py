import time

def wait(seconds: int=1):
    animation = "|/-\\"
    id = 0
    end = time.time() + seconds
    while end > time.time():
        print(animation[id % len(animation)], end="\r")
        id += 1
        time.sleep(0.1)


wait(3)