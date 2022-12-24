from .elf import Elf


class ElfGrid:
  def __init__(self, n, m) -> None:
    self.grid = {}
    self.n = n
    self.m = m
    # self.proposal_order = [(0, 1), (0, -1), (-1, 0), (1, 0)]
    self.proposal_order = ["N", "S", "W", "E"]
    self.dir_step_map = {
        "N": (0, 1),
        "E": (1, 0),
        "W": (-1, 0),
        "S": (0, -1)
    }
    self.dirs_to_check_map = {
        "N": [(-1, 1), (0, 1), (1, 1)],
        "E": [(1, 1), (1, 0), (1, -1)],
        "W": [(-1, 1), (-1, 0), (-1, -1)],
        "S": [(-1, -1), (0, -1), (1, -1)]
    }

  def get_range(self):
    min_x = min(self.grid.keys(), key=lambda x: x[0])[0]
    max_x = max(self.grid.keys(), key=lambda x: x[0])[0]
    min_y = min(self.grid.keys(), key=lambda x: x[1])[1]
    max_y = max(self.grid.keys(), key=lambda x: x[1])[1]
    return ((min_x, max_x), (min_y, max_y))

  def __repr__(self) -> str:
    x_range, y_range = self.get_range()
    min_x, max_x = x_range
    min_y, max_y = y_range
    s = ""
    for y in range(min_y, max_y + 1):
      for x in range(min_x, max_x + 1):
        s += str(self.grid.get((x, y), "."))
      s += "\n"
    return s

  def get_area_spanning_rectangle(self):
    x_range, y_range = self.get_range()
    min_x, max_x = x_range
    min_y, max_y = y_range

    return (1+max_x-min_x) * (1+max_y-min_y)

  def get_proposal_order(self):
    return self.proposal_order

  def rotate_proposal_order(self):
    self.proposal_order = self.proposal_order[1:] + [self.proposal_order[0]]
    return self.proposal_order

  def add_elf(self, x, y):
    elf = Elf()
    elf.set_pos(x, y)
    self.grid[(x, y)] = elf

  def get_elf(self, x, y):
    return self.grid.get((x, y), None)

  def get_neighbours_of_elf(self, elf):
    x, y = elf.get_pos()
    neighbours = []
    for dx, dy in [
        (0, 1), (1, 0), (0, -1), (-1, 0),
        (1, 1), (1, -1), (-1, 1), (-1, -1)
    ]:
      if (x + dx, y + dy) in self.grid:
        neighbours.append(self.grid[(x + dx, y + dy)])
    return neighbours

  def check_pos_empty(self, pos):
    return self.grid.get(pos) is None

  def get_dirs_to_check(self, dir):
    return self.dirs_to_check_map[dir]

  def check_dir_empty(self, elf: Elf, dir) -> bool:
    """
    check if the proposed move is 
    """
    pos = elf.get_pos()
    dirs_to_check = self.get_dirs_to_check(dir)
    for dir in dirs_to_check:
      new_pos = (pos[0] + dir[0], pos[1] + dir[1])
      if self.check_pos_empty(new_pos):
        return True
    return False

  def compute_elf_proposal_dir(self, elf):
    for direction in self.proposal_order:
      if self.check_dir_empty(elf, direction):
        return direction
    return None

  def get_proposal_grid(self):
    for pos in self.grid.keys():
      elf: Elf = self.grid[pos]
      proposed_direction = self.compute_elf_proposal_dir(elf)
      if proposed_direction is not None:
        proposed_step = self.dir_step_map[proposed_direction]
        proposed_pos = (pos[0] + proposed_step[0], pos[1] + proposed_step[1])
      else:
        proposed_pos = pos
      elf.set_proposal(proposed_pos)

      print(elf.to_string(), proposed_direction)

  def move_elves(self):
    new_grid = self.get_proposal_grid()
    # self.grid = new_grid
    self.rotate_proposal_order()
