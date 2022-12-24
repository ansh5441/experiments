from helper.elf_grid import ElfGrid
from helper.elf import Elf


def get_grid(input_data):
  n = len(input_data)
  m = len(input_data[0])
  grid = ElfGrid(n, m)
  for y in range(n):
    for x in range(m):
      if input_data[y][x] == "#":
        grid.add_elf(x, y)
  return grid


def solve(input_data):
  grid = get_grid(input_data)
  print(grid)
  round = 0
  while True:
    round += 1
    if round % 100 == 0:
      print(round)
      print(grid)
    num_to_move = grid.move_elves()
    print(round, num_to_move)
    if num_to_move == 0:
      break
  print(grid)
  return round


if __name__ == "__main__":
  input_file = "advent_of_code/2022/day_23/input/input.txt"
  with open(input_file) as f:
    input_data = [line.strip() for line in f.readlines()]
    sol = solve(input_data)
    print(sol)
