import math


class Elf:
  def __init__(self) -> None:
    self.x = math.inf
    self.y = math.inf
    self.proposal = None

  def set_pos(self, x, y):
    self.x = x
    self.y = y

  def get_pos(self):
    return (self.x, self.y)

  def set_proposal(self, pos):
    self.proposal = pos

  def get_proposal(self):
    return self.proposal

  def move_to_proposed_position(self):
    prop = self.get_proposal()
    if prop is not None:
      propx, propy = prop
      self.set_pos(propx, propy)

  def __repr__(self) -> str:
    # return f"{self.get_pos()}"
    return "#"

  def to_string(self) -> str:
    return f"#: {self.get_pos()} -> {self.get_proposal()}"
