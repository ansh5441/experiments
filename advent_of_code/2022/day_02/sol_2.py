from enum import Enum

input_file = "advent_of_code/2022/day_02/input/input"


class Entity(Enum):
  ROCK = 1
  PAPER = 2
  SCISSORS = 3


SCORE_FOR_WIN = 6
SCORE_FOR_DRAW = 3
SCORE_FOR_LOSS = 0


RPS_DEFAULT_SCORE = {
    Entity.ROCK: 1,
    Entity.PAPER: 2,
    Entity.SCISSORS: 3
}

RPS_CODE = {
    "A": Entity.ROCK,
    "B": Entity.PAPER,
    "C": Entity.SCISSORS,
}

RPS_WINNER = {
    Entity.ROCK: Entity.PAPER,
    Entity.PAPER: Entity.SCISSORS,
    Entity.SCISSORS: Entity.ROCK
}

RPS_WIN_LOSE = {
    Entity.PAPER: {"X": Entity.ROCK, "Y": Entity.PAPER, "Z": Entity.SCISSORS},
    Entity.ROCK: {"X": Entity.SCISSORS, "Y": Entity.ROCK, "Z": Entity.PAPER},
    Entity.SCISSORS: {"X": Entity.PAPER, "Y": Entity.SCISSORS, "Z": Entity.ROCK},
}


def get_winner(player_1, player_2):
  if player_1 == player_2:
    return 0
  elif RPS_WINNER[player_1] == player_2:
    return 1
  else:
    return 2


def get_player_2_move(p1, p2):

  return RPS_WIN_LOSE[RPS_CODE[p1]][p2]


def get_player2_score(player_1, player_2):
  winner = get_winner(RPS_CODE[player_1], player_2)
  score = RPS_DEFAULT_SCORE[player_2]
  if winner == 0:
    score += SCORE_FOR_DRAW
  elif winner == 1:
    score += SCORE_FOR_WIN
  else:
    score += SCORE_FOR_LOSS
  return score


with open(input_file) as f:
  input = f.read().splitlines()
  score = 0
  for moves in input:
    p1, p2 = moves.split()
    score += get_player2_score(p1, get_player_2_move(p1, p2))
  print(score)
