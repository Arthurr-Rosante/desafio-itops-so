from numpy import random

CHARACTERS = "ABCDEFGHIJKLMNPQRSTUVWXYZ123456789"
def gen_random_id(prefix, length = 12):
    size = length - len(prefix)
    id = prefix

    for _ in range(size):
        id += CHARACTERS[random.randint(size)] 
    return id