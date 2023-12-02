from pprint import pprint


def get_heights(data):
  heights = []
  for line in data:
    heights.append([])
    for tree in line:
      heights[-1].append(int(tree))
  return heights


def get_visible_grid(heights):
  n = len(heights)
  m = len(heights[0])
  return [[0 for i in range(m)] for j in range(n)]


def get_left_max_heights(heights):
  left_max_heights = []
  n = len(heights)
  m = len(heights[0])
  for i in range(n):
    left_max_heights.append([])
    for j in range(m):
      if j == 0:
        left_max_heights[i].append(heights[i][j])
      else:
        left_max_heights[i].append(
            max(left_max_heights[i][j - 1], heights[i][j]))
  return left_max_heights


def get_right_max_heights(heights):
  n = len(heights)
  m = len(heights[0])
  right_max_heights = [[-1 for i in range(m)] for j in range(n)]
  for i in range(n):
    for j in range(m-1, -1, -1):
      if j == m - 1:
        right_max_heights[i][j] = heights[i][j]
      else:
        right_max_heights[i][j] = (
            max(right_max_heights[i][j + 1], heights[i][j]))
  return right_max_heights


def get_top_max_heights(heights):
  n = len(heights)
  m = len(heights[0])
  top_max_heights = [[-1 for i in range(m)] for j in range(n)]
  for i in range(n):
    for j in range(m):
      if i == 0:
        top_max_heights[i][j] = heights[i][j]
      else:
        top_max_heights[i][j] = (
            max(top_max_heights[i - 1][j], heights[i][j]))
  return top_max_heights


def get_bottom_max_heights(heights):
  n = len(heights)
  m = len(heights[0])
  bottom_max_heights = [[-1 for i in range(m)] for j in range(n)]
  for i in range(n-1, -1, -1):
    for j in range(m):
      if i == n - 1:
        bottom_max_heights[i][j] = heights[i][j]
      else:
        bottom_max_heights[i][j] = (
            max(bottom_max_heights[i + 1][j], heights[i][j]))
  return bottom_max_heights


def pg(trees):
  print()
  for row in trees:
    print(row)


def find_num_visible_trees(heights):
  n = len(heights)
  m = len(heights[0])
  visible_grid = get_visible_grid(heights)
  left_max_heights = get_left_max_heights(heights)
  pg(left_max_heights)
  right_max_heights = get_right_max_heights(heights)
  pg(right_max_heights)
  top_max_heights = get_top_max_heights(heights)
  pg(top_max_heights)
  bottom_max_heights = get_bottom_max_heights(heights)
  pg(bottom_max_heights)
  for i in range(n):
    for j in range(m):
      if i == 0 or i == n - 1 or j == 0 or j == m - 1:
        visible_grid[i][j] = 1
      else:
        visible_left = left_max_heights[i][j] <= heights[i][j] and left_max_heights[i][j -
                                                                                       1] < left_max_heights[i][j]
        visible_right = right_max_heights[i][j] <= heights[i][j] and right_max_heights[i][j +
                                                                                          1] < right_max_heights[i][j]
        visible_top = top_max_heights[i][j] <= heights[i][j] and top_max_heights[i -
                                                                                 1][j] < top_max_heights[i][j]

        visible_bottom = bottom_max_heights[i][j] <= heights[i][j] and bottom_max_heights[i +
                                                                                          1][j] < bottom_max_heights[i][j]

        if visible_bottom or visible_top or visible_left or visible_right:
          visible_grid[i][j] = 1
  pg(visible_grid)
  return sum([sum(row) for row in visible_grid])


input_file = "advent_of_code/2022/day_08/input/input"
# input_file = "advent_of_code/2022/day_08/input/sample"
with open(input_file) as f:
  data = f.read().splitlines()
  pg(data)
  heights = get_heights(data)
  num_visible_trees = find_num_visible_trees(heights)
  print(num_visible_trees)
