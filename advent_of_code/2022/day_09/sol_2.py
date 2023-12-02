input_file = "advent_of_code/2022/day_09/input/input"


def parse_input(data):
  movements = []
  for line in data:
    line = line.split()
    movements.append((line[0], int(line[1])))
  return movements


def move_tail(head, tail):
  hx, hy = head
  tx, ty = tail
  dx, dy = hx - tx, hy - ty
  # is okay
  if abs(dx) <= 1 and abs(dy) <= 1:
    return tail
  # same row
  elif dx == 0 and abs(dy) > 1:
    ty += dy // abs(dy)
  # same column
  elif dy == 0 and abs(dx) > 1:
    tx += dx // abs(dx)
  # diagonal
  else:
    tx += dx // abs(dx)
    ty += dy // abs(dy)
  return [tx, ty]


def execute_move(head, move):
  direction, distance = move
  hx, hy = head
  if distance == 0:
    return head
  else:
    if direction == "U":
      hy += 1
    elif direction == "D":
      hy -= 1
    elif direction == "R":
      hx += 1
    elif direction == "L":
      hx -= 1
    return [hx, hy]


def get_all_visited_locations(movements):
  knots = [[0, 0] for i in range(10)]
  visited_locations = set()
  for move in movements:
    for step in range(move[1]):
      knots[0] = execute_move(knots[0], (move[0], 1))
      for i in range(1, 10):
        knots[i] = move_tail(knots[i-1], knots[i])
      visited_locations.add(tuple(knots[9]))
  return visited_locations


with open(input_file) as f:
  data = f.read().splitlines()
  movements = parse_input(data)
  visited_locs = get_all_visited_locations(movements)
  print(len(visited_locs))
