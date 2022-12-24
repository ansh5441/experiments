from helper.monkey import Monkey
from pprint import pprint


def create_monkeys(data):
  monkeys = []
  curr_monkey = Monkey(-1)
  for line in data:
    if line.startswith("Monkey"):
      num = int(line.split(" ")[1][:-1])
      curr_monkey = Monkey(num)
      monkeys.append(curr_monkey)
    if line.startswith("  Starting items: "):
      items = line.split()[2:]
      for item in items:
        if item.endswith(","):
          item = item[:-1]
        curr_monkey.add_starting_item(int(item))
    if line.startswith("  Operation:"):
      op = line.split()[-2:]
      curr_monkey.op = op
    if line.startswith("  Test: "):
      test = line.split()[-1]
      curr_monkey.test = int(test)
    if line.startswith("    If true: "):
      test_true = line.split()[-1]
      curr_monkey.test_true = int(test_true)
    if line.startswith("    If false: "):
      test_false = line.split()[-1]
      curr_monkey.test_false = int(test_false)
  return monkeys


input_file = "advent_of_code/2022/day_11/input/input"
with open(input_file) as f:
  data = f.read().splitlines()
  monkeys = create_monkeys(data)
  pprint(monkeys)
