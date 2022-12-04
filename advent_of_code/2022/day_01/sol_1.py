input_file = "advent_of_code/2022/day_01/input/input"
with open(input_file) as f:
  data = f.read().splitlines()
  elf_energy = [0]
  for d in data:
    if d == "":
      elf_energy.append(0)
    else:
      elf_energy[-1] += int(d)
print(max(elf_energy))
