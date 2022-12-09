from pprint import pprint


class File:
  def __init__(self, name, size):
    self.name = name
    self.size = size

  def __repr__(self):
    return f"{self.name}"


class Dir:
  def __init__(self, name, parent):
    self.name = name
    self.parent = parent
    self.subdirs = []
    self.files = []
    self.size = None

  def add_subdir(self, subdir):
    self.subdirs.append(subdir)

  def add_file(self, file):
    self.files.append(file)

  def calculate_size(self):
    if self.size is None:
      self.size = sum([file.size for file in self.files])
      for subdir in self.subdirs:
        self.size += subdir.calculate_size()
    return self.size


def create_dir_tree(data):
  curr_dir = Dir("/", None)
  for line in data[1:]:
    if line.startswith("$ ls"):
      continue
    if line.startswith("$ cd"):
      next_dir_name = line.split(" ")[2]
      if next_dir_name == "..":
        curr_dir = curr_dir.parent
      else:
        for subdir in curr_dir.subdirs:
          if subdir.name == next_dir_name:
            curr_dir = subdir
            break
    elif line.startswith("dir"):
      dir_name = line.split(" ")[1]
      new_dir = Dir(dir_name, curr_dir)
      curr_dir.add_subdir(new_dir)
    else:
      file_size, file_name = line.split(" ")
      new_file = File(file_name, int(file_size))
      curr_dir.add_file(new_file)

  while curr_dir.parent is not None:
    curr_dir = curr_dir.parent
  return curr_dir


def find_smallest_dir_to_delete(root_dir, smallest_size):
  globarr = []

  def find_smallest_dir(root_dir, smallest_size):
    if root_dir.calculate_size() > smallest_size:
      globarr.append(root_dir.calculate_size())
    for subdir in root_dir.subdirs:
      find_smallest_dir(subdir, smallest_size)
  find_smallest_dir(root_dir, smallest_size)
  return min(globarr)


input_file = "advent_of_code/2022/day_07/input/input.txt"
with open(input_file) as f:
  data = f.read().splitlines()
  root_dir = create_dir_tree(data)
  if root_dir is not None:
    print(root_dir.calculate_size())
    remaining_space = 70000000 - root_dir.calculate_size()
    required_space = 30000000
    additional_space = required_space - remaining_space
    print(f"Additional space required: {additional_space}")
    smallest_dir = find_smallest_dir_to_delete(
        root_dir, additional_space)
    print(f"Smallest dir to delete: {smallest_dir.calculate_size()}")
