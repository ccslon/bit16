baz:
  PUSH B, FP
  MOV FP, SP
  LD A, [FP, 2] ; y
  LD B, [FP, 3] ; z
  MUL A, B
  JR .L0
.L0:
  MOV SP, FP
  POP B, FP
  ADD SP, 2
  RET
bar:
  PUSH B, FP
  MOV FP, SP
  LD A, [FP, 2] ; x
  LD B, [FP, 3] ; y
  MUL A, B
  JR .L1
.L1:
  MOV SP, FP
  POP B, FP
  ADD SP, 2
  RET
foo:
  PUSH LR, B, C, FP
  MOV FP, SP
  LD B, [FP, 5] ; y
  PUSH B
  LD B, [FP, 4] ; x
  PUSH B
  CALL bar
  MOV B, A
  LD C, [FP, 6] ; z
  PUSH C
  LD C, [FP, 5] ; y
  PUSH C
  CALL baz
  MOV C, A
  ADD B, C
  JR .L2
.L2:
  MOV A, B
  MOV SP, FP
  POP LR, B, C, FP
  ADD SP, 3
  RET