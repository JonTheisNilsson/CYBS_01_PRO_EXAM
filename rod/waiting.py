import time


ani1 = "|/-\\"
ani2 = [' 👧⚽️       👦', '👧  ⚽️      👦', '👧   ⚽️     👦', '👧    ⚽️    👦', '👧     ⚽️   👦', '👧      ⚽️  👦', '👧      ⚽️👦 ', '👧      ⚽️  👦', '👧     ⚽️   👦', '👧    ⚽️    👦', '👧   ⚽️     👦', '👧  ⚽️      👦']
ani3 = ['🕛', '🕐', '🕑', '🕒', '🕓', '🕔', '🕕', '🕖', '🕗', '🕘', '🕙', '🕚']

def wait(seconds: int, animation:str|list):
    #animation = "|/-\\"
    id = 0
    end = time.time() + seconds
    
    print('\033[?25l', end="") # make cursor invisible,  see "ANSI Escape Sequences"

    while end > time.time():
        print(animation[id % len(animation)], end="\r")
        id += 1
        time.sleep(0.1)

    print('\033[?25h', end="") # make cursor visible"


wait(10, ani3)
