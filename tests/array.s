foo:
  PUSH A, B, C, FP
  SUB SP, 9
  MOV FP, SP
  MOV A, 2
  ST [FP, 5], A ; i
  MOV A, 2
  ADD B, FP, 0
  LD C, [FP, 5] ; i
  ADD B, C
  ST [B], A
  ADD A, FP, 6
  MOV B, 1
  ST [A, 0], B
  MOV B, 2
  ST [A, 1], B
  MOV B, 3
  ST [A, 2], B
  MOV SP, FP
  ADD SP, 9
  POP A, B, C, FP
  RET