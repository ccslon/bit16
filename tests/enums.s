main:
  PUSH FP
  SUB SP, 2
  MOV FP, SP
  MOV A, 10
  LD [FP, 0], A ; day
  MOV A, 4
  LD [FP, 1], A ; today
  MOV A, 0
  JR .L0
.L0:
  MOV SP, FP
  ADD SP, 2
  POP FP
  RET