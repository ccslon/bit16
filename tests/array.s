foo:
  PUSH A, B, C, FP
  SUB SP, 9
  MOV FP, SP
  MOV A, 2
  LD [FP, 5], A ; i
  MOV A, 2
  ADD B, FP, 0
  LD C, [FP, 5] ; i
  ADD B, C
  LD [B], A
  ADD A, FP, 6
  MOV B, 1
  LD [A, 0], B
  MOV B, 2
  LD [A, 1], B
  MOV B, 3
  LD [A, 2], B
  MOV SP, FP
  ADD SP, 9
  POP A, B, C, FP
  RET