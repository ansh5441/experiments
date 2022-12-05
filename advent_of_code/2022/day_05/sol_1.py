from collections import defaultdict
from pprint import pprint
input_file = "advent_of_code/2022/day_05/input/input"


def create_stacks_from_input(stack_input):
  stacks_dict = defaultdict(list)
  for line in stack_input:
    n = len(line)
    for i in range(0, n, 4):
      content = line[i+1:i+2]
      if 65 <= ord(content) <= 90:
        stacks_dict[1 + i//4].append(content)
  for key in stacks_dict:
    stacks_dict[key].reverse()
  return stacks_dict


def execute_instructions(stacks_dict, instruction):
  """
  modify dict in place

  """
  instruction = instruction.split()
  n = int(instruction[1])
  from_stack = int(instruction[3])
  to_stack = int(instruction[5])
  for i in range(n):
    stacks_dict[to_stack].append(stacks_dict[from_stack].pop())


with open(input_file) as f:
  data = f.read().splitlines()
  stack_input = []
  instructions = []
  switch = False
  for line in data:
    if line == '':
      switch = True
      continue
    if switch == False:
      stack_input.append(line)

    if switch == True:
      instructions.append(line)
  stacks = create_stacks_from_input(stack_input)
  for instruction in instructions:
    execute_instructions(stacks, instruction)
  pprint(stacks)
  for i in range(1, 10):
    print(stacks[i][-1], end='')
