foo: 9
test:
  PUSH A, B, FP
  SUB SP, 1
  MOV FP, SP
  MOV A, 10
  LD B, 100
  MUL A, B
  LD [FP, 0], A ; num
  MOV SP, FP
  ADD SP, 1
  POP A, B, FP
  RET