main:
  SUB SP, 2
  MOV FP, SP
  MOV A, 10
  LD [FP, 0], A ; day
  MOV A, 4
  LD [FP, 1], A ; today
  MOV SP, FP
  ADD SP, 2
  HALT