input_file = "advent_of_code/2022/day_06/input/input"


def find_code_start(data):
  for i, char in enumerate(data):
    if len(set(data[i:i+4])) == 4:
      return i+4
    


with open(input_file) as f:
  data = f.read()
  print(find_code_start(data))
