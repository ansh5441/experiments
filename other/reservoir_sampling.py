import sys
import random
 
def get_reservoir_sample(N,arr):
    sample = []

    for i,line in enumerate(arr):
        if i < N:
            sample.append(line)
        elif i >= N and random.random() < N/float(i+1):
            replace = random.randint(0,len(sample)-1)
            sample[replace] = line
    return sample
     

if __name__ == "__main__":
    n = 3
    arr = '0123456789'
    num_test = 10000
    dic = {}
    for i in range(num_test):
        res = get_reservoir_sample(n,arr)
        for r in res:
            if dic.get(r) is None:
                dic[r] = 1
            else:
                dic[r] += 1
    for d in arr:
        print(d,end = ' ')
        for i in range(int(dic[d]/40)):
            print('*',end='')
        print()

