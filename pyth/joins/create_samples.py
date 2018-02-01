import random
SIZE = 650000

def generate_arr():
    count = 0
    index = 1000
    arr = []
    while count < SIZE:
        index += 1
        if random.random() < 0.4:
            count += 1
            arr.append(index)
    return arr

f = open('sample.txt','w')

first_arr = generate_arr()
second_arr = generate_arr()


for a,b in zip(first_arr, second_arr):
    f.write(str(a) + ' ' + str(b) + '\n')

f.close()