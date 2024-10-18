multi:
  PUSH A, B, FP
  SUB SP, 3
  MOV FP, SP
  MOV A, 3
  ST [FP, 0], A ; foo
  MOV A, 2
  LD B, [FP, 0] ; foo
  SUB A, B
  ST [FP, 1], A ; bar
  LD A, [FP, 1] ; bar
  LD B, [FP, 0] ; foo
  MUL B, 4
  ADD A, B
  ST [FP, 2], A ; baz
  MOV SP, FP
  ADD SP, 3
  POP A, B, FP
  RET