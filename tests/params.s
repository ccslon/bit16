params0:
  PUSH FP
  MOV FP, SP
  MOV A, 0
  JR .L0
.L0:
  MOV SP, FP
  POP FP
  RET
params1:
  PUSH FP
  MOV FP, SP
  LD A, [FP, 1] ; foo
  JR .L1
.L1:
  MOV SP, FP
  POP FP
  ADD SP, 1
  RET
params2:
  PUSH B, FP
  MOV FP, SP
  LD A, [FP, 2] ; foo
  LD B, [FP, 3] ; bar
  ADD A, B
  JR .L2
.L2:
  MOV SP, FP
  POP B, FP
  ADD SP, 2
  RET
params3:
  PUSH B, FP
  MOV FP, SP
  LD A, [FP, 2] ; foo
  LD B, [FP, 3] ; bar
  ADD A, B
  LD B, [FP, 4] ; baz
  ADD A, B
  JR .L3
.L3:
  MOV SP, FP
  POP B, FP
  ADD SP, 3
  RET