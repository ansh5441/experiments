
input_file = "advent_of_code/2022/day_06/input/input"


def find_message_start(data):
  m_len = 14
  for i, char in enumerate(data):
    if len(set(data[i:i+m_len])) == m_len:
      return i+m_len
    


with open(input_file) as f:
  data = f.read()
  print(find_message_start(data))
