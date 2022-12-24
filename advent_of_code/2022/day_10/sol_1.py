input_file = "advent_of_code/2022/day_10/input/input.txt"

interesting_cycles = [
    20, 60, 100, 140, 180, 220
]


def parse_input(data):
  instructions = []
  for line in data:
    line = line.split()
    if line[0] == "noop":
      instructions.append(line[0])
    else:
      instructions.append((line[0], int(line[1])))
  return instructions


def get_X_during_cycle(instructions):
  x_val = 1
  x_vals = [0]
  for ins in instructions:
    if ins == "noop":
      x_vals.append(x_val)
    else:
      x_vals.append(x_val)
      x_vals.append(x_val)
      x_val = x_val + ins[1]
  return x_vals


def get_interesting_x_vals(x_vals):
  sum_x = 0
  for c in interesting_cycles:
    sum_x += x_vals[c] * c
  return sum_x


with open(input_file) as f:
  data = f.read().splitlines()
  instructions = parse_input(data)
  print(instructions)
  get_x_vals = get_X_during_cycle(instructions)
  print(get_interesting_x_vals(get_x_vals))
