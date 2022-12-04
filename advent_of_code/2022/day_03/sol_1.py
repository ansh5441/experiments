from collections import defaultdict


def convert_item_priority_score(chr):
  asc = ord(chr)
  if asc >= 65 and asc <= 90:
    return asc - 64 + 26
  elif asc >= 97 and asc <= 122:
    return asc - 96
  return 0


def find_item_in_both_compartments(bag: str):
  compartment_1_size = len(bag) // 2
  compartment_1_set = set([bag[i] for i in range(compartment_1_size)])
  for i in range(compartment_1_size, len(bag)):
    if bag[i] in compartment_1_set:
      return bag[i]


input_file = "advent_of_code/2022/day_03/input/input"
with open(input_file) as f:
  data = f.read().splitlines()
  priority_sum = 0
  for bag in data:
    repeated_item = find_item_in_both_compartments(bag)
    priority_sum += convert_item_priority_score(repeated_item)
  print(priority_sum)
