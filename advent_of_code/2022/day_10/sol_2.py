input_file = "advent_of_code/2022/day_10/input/input.txt"


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


def draw(x_vals):
  n = len(x_vals)
  res = ""
  for i in range(1, n):
    row = i // 40
    col = (i-1) % 40
    if x_vals[i] in [col-1, col, col+1]:
      res += "#"
    else:
      res += "."
    if i % 40 == 0:
      res += "\n"
  return res


with open(input_file) as f:
  data = f.read().splitlines()
  instructions = parse_input(data)
  get_x_vals = get_X_during_cycle(instructions)
  res = draw(get_x_vals)
  print(res)
