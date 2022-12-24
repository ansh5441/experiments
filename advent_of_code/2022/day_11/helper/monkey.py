class Monkey:
  def __init__(self, num) -> None:
    self.num = num
    self.starting_item = []
    self.op = None
    self.test = 1
    self.test_true = -1
    self.test_false = -1

  def __repr__(self) -> str:
    return f"Monkey {self.num}\t op: {self.op}\t test: {self.test}\t test_true: {self.test_true}\t test_false: {self.test_false}\t items: {self.starting_item}"

  def add_starting_item(self, item):
    self.starting_item.append(item)

  def inspect_items(self):
    for item in self.starting_item:
      print(item)
