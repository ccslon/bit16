foo:
  PUSH FP
  MOV FP, SP
  LD A, [FP, 1] ; bar
  CMP A, 3
  JLE .L1
  MOV A, 3
  ST [FP, 1], A ; bar
  JR baz
.L1:
  LD A, [FP, 1] ; bar
  MUL A, 3
  ST [FP, 1], A ; bar
baz:
  LD A, [FP, 1] ; bar
  JR .L0
.L0:
  MOV SP, FP
  POP FP
  ADD SP, 1
  RET