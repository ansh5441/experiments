def get_heights(data):
  heights = []
  for line in data:
    heights.append([])
    for tree in line:
      heights[-1].append(int(tree))
  return heights


def get_scores(heights):
  n = len(heights)
  m = len(heights[0])
  return [[0 for i in range(m)] for j in range(n)]


def pg(trees):
  print()
  for row in trees:
    print(row)


def compute_left_visibility(heights):
  n = len(heights)
  m = len(heights[0])
  left_visibility_matrix = get_scores(heights)
  for i in range(n):
    for j in range(m):
      if j == 0:
        left_visibility_matrix[i][j] = 0
      else:
        k = j-1
        while k > 0 and heights[i][k] < heights[i][j]:
          k -= 1
        left_visibility_matrix[i][j] = j - k
  return left_visibility_matrix


def compute_right_visibility(heights):
  n = len(heights)
  m = len(heights[0])
  right_visibility_matrix = get_scores(heights)
  for i in range(n):
    for j in range(m-1, -1, -1):
      if j == m-1:
        right_visibility_matrix[i][j] = 0
      else:
        k = j+1
        while k < m-1 and heights[i][k] < heights[i][j]:
          k += 1
        right_visibility_matrix[i][j] = k - j
  return right_visibility_matrix


def compute_top_visibility(heights):
  n = len(heights)
  m = len(heights[0])
  top_visibility_matrix = get_scores(heights)
  for i in range(n):
    for j in range(m):
      if i == 0:
        top_visibility_matrix[i][j] = 0
      else:
        k = i-1
        while k > 0 and heights[k][j] < heights[i][j]:
          k -= 1
        top_visibility_matrix[i][j] = i - k

  return top_visibility_matrix


def compute_bottom_visibility(heights):
  n = len(heights)
  m = len(heights[0])
  bottom_visibility_matrix = get_scores(heights)
  for i in range(n-1, -1, -1):
    for j in range(m):
      if i == n-1:
        bottom_visibility_matrix[i][j] = 0
      else:
        k = i+1
        while k < n-1 and heights[k][j] < heights[i][j]:
          k += 1
        bottom_visibility_matrix[i][j] = k - i
  return bottom_visibility_matrix


def find_max_scenic_score(heights):
  n = len(heights)
  m = len(heights[0])
  left_scores = compute_left_visibility(heights)
  right_scores = compute_right_visibility(heights)
  top_scores = compute_top_visibility(heights)
  bottom_scores = compute_bottom_visibility(heights)
  max_score = 0
  for i in range(n):
    for j in range(m):
      curr_score = left_scores[i][j] * right_scores[i][j] * \
          top_scores[i][j] * bottom_scores[i][j]
      if curr_score > max_score:
        print(i, j, curr_score, left_scores[i][j], right_scores[i]
              [j], top_scores[i][j], bottom_scores[i][j])
        max_score = curr_score
  return max_score


input_file = "advent_of_code/2022/day_08/input/input"
# input_file = "advent_of_code/2022/day_08/input/sample"
with open(input_file) as f:
  data = f.read().splitlines()
  pg(data)
  heights = get_heights(data)
  num_visible_trees = find_max_scenic_score(heights)
  print(num_visible_trees)
