from collections import defaultdict


def convert_item_priority_score(chr):
  asc = ord(chr)
  if asc >= 65 and asc <= 90:
    return asc - 64 + 26
  elif asc >= 97 and asc <= 122:
    return asc - 96
  return 0


def find_item_in_3_bags(bag_1: str, bag_2: str, bag_3: str):
  item_bag_no = defaultdict(set)
  for item in bag_1:
    item_bag_no[item].add(1)
  for item in bag_2:
    item_bag_no[item].add(2)
  for item in bag_3:
    item_bag_no[item].add(3)
  for item, bag_set in item_bag_no.items():
    if len(bag_set) == 3:
      return item


input_file = "advent_of_code/2022/day_03/input/input"
with open(input_file) as f:
  data = f.read().splitlines()
  priority_sum = 0
  for i in range(0, len(data), 3):
    repeated_item = find_item_in_3_bags(data[i], data[i + 1], data[i + 2])
    priority_sum += convert_item_priority_score(repeated_item)
  print(priority_sum)
