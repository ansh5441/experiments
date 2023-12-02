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


def find_sum_of_dir_sizes_lt_100000(root_dir):
  threshold = 100000
  sum_sizes = root_dir.size if root_dir.size < threshold else 0
  for subdir in root_dir.subdirs:
    sum_sizes += find_sum_of_dir_sizes_lt_100000(subdir)
  return sum_sizes

input_file = "advent_of_code/2022/day_07/input/input.txt"
with open(input_file) as f:
  data = f.read().splitlines()
  root_dir = create_dir_tree(data)
  if root_dir is not None:
    print(root_dir.calculate_size())
    print(find_sum_of_dir_sizes_lt_100000(root_dir))
