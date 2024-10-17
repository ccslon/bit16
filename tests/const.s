foo:
  PUSH A, FP
  SUB SP, 1
  MOV FP, SP
  MOV A, 3
  ST [FP, 0], A ; foo
  MOV SP, FP
  ADD SP, 1
  POP A, FP
  RET