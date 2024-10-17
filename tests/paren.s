paren:
  PUSH A, B, FP
  SUB SP, 4
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
  LD A, [FP, 0] ; foo
  LD B, [FP, 1] ; bar
  ADD A, B
  NEG A
  LD B, [FP, 2] ; baz
  ADD B, 10
  MUL A, B
  ST [FP, 3], A ; bif
  MOV SP, FP
  ADD SP, 4
  POP A, B, FP
  RET