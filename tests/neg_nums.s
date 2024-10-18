foo:
  PUSH A, FP
  SUB SP, 3
  MOV FP, SP
  MOV A, -3
  ADD A, 4
  ST [FP, 0], A ; n
  MOV A, 3
  ADD A, 4
  NEG A
  ST [FP, 1], A ; m
  MOV A, 3
  ADD A, -4
  NEG A
  ST [FP, 2], A ; o
  MOV SP, FP
  ADD SP, 3
  POP A, FP
  RET