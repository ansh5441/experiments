input_file = "advent_of_code/2022/day_04/input/input"


def range_1_in_range_2(range_1: list, range_2: list) -> bool:
  return range_1[0] >= range_2[0] and range_1[1] <= range_2[1]


with open(input_file) as f:
  data = f.read().splitlines()
  contained_range_count = 0
  for ranges in data:
    elf1, elf2 = ranges.split(",")
    elf1 = [int(e) for e in elf1.split("-")]
    elf2 = [int(e) for e in elf2.split("-")]
    if range_1_in_range_2(elf1, elf2) or range_1_in_range_2(elf2, elf1):
      contained_range_count += 1
  print(contained_range_count)
