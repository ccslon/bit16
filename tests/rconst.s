rconst:
  PUSH A, B, FP
  SUB SP, 2
  MOV FP, SP
  MOV A, 3
  LD [FP, 0], A ; foo
  MOV A, 2
  LD B, [FP, 0] ; foo
  SUB A, B
  LD [FP, 1], A ; bar
  MOV SP, FP
  ADD SP, 2
  POP A, B, FP
  RET