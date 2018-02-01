import time
def read_arr(file_name):
	arr_1 = []
	arr_2 = []
	f = open(file_name, 'r')
	l = f.readline()
	while l not in ('', None):
		l = l.split()
		arr_1.append(l[0])
		arr_2.append(l[1])
		l = f.readline()
	f.close()

	return arr_1, arr_2

def find_matches(arr_1, arr_2):
	i = 0
	j = 0
	len_1 = len(arr_1)
	len_2 = len(arr_2)
	match_arr = []
	while i < len_1 and j < len_2:
		if arr_1[i] < arr_2[j]:
			i += 1
		elif arr_1[i] > arr_2[j]:
			j += 1
		else:
			match_arr.append(arr_1[i])
			i += 1
			j += 1
	return match_arr


if __name__ == '__main__':
	arr_1, arr_2 = read_arr('sample.txt')
	SAMPLE_SIZE = 10
	total_time = 0
	for i in range(SAMPLE_SIZE): 
		t1 = time.time()
		match_size = find_matches(arr_1, arr_2)
		t2 = time.time()
		total_time += t2-t1
	print("from arrays of size =  " + str(len(arr_1)) + 
		"\nnumber of common elements =  " + str(len(match_size)) + 
		"\ntime taken = " + str(total_time/SAMPLE_SIZE)[:7])

