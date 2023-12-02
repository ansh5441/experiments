from math import inf
input_file = "advent_of_code/2022/day_12/input/input"
# input_file = "advent_of_code/2022/day_12/input/input_test"


def get_next_steps(i, j, heights):
  n = len(heights)
  m = len(heights[0])
  for di, dj in [(0, 1), (0, -1), (1, 0), (-1, 0)]:
    new_i = i + di
    new_j = j + dj
    if 0 <= new_i < n and 0 <= new_j < m:
      if heights[new_i][new_j] - heights[i][j] <= 1:
        yield new_i, new_j


def dijkstras_shortest_path(start_point, end_point, heights):
  n = len(heights)
  m = len(heights[0])
  dist = [[inf] * m for _ in range(n)]
  dist[start_point[0]][start_point[1]] = 0
  visited = [[False] * m for _ in range(n)]
  while True:
    min_dist = inf
    min_i = None
    min_j = None
    for i in range(n):
      for j in range(m):
        if not visited[i][j] and dist[i][j] < min_dist:
          min_dist = dist[i][j]
          min_i = i
          min_j = j
    if min_i is None:
      break
    visited[min_i][min_j] = True
    for next_i, next_j in get_next_steps(min_i, min_j, heights):
      new_dist = dist[min_i][min_j] + 1
      if new_dist < dist[next_i][next_j]:
        dist[next_i][next_j] = new_dist
  return dist[end_point[0]][end_point[1]]

def find_shortest_path(data):
  n = len(data)
  m = len(data[0])
  start_point = None
  end_point = None
  heights = [[0] * m for _ in range(n)]
  for i, line in enumerate(data):
    for j, char in enumerate(line):
      if char == "S":
        start_point = (i, j)
        heights[i][j] = inf
      elif char == "E":
        end_point = (i, j)
        heights[i][j] = -inf
      else:
        heights[i][j] = ord(char) - ord("a")
  pl = dijkstras_shortest_path(start_point, end_point, heights)
  print(pl)


with open(input_file) as f:
  data = f.read().splitlines()
  find_shortest_path(data)
