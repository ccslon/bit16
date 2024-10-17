sqr:
  PUSH B, FP
  MOV FP, SP
  LD A, [FP, 2] ; n
  LD B, [FP, 2] ; n
  MUL A, B
  JR .L0
.L0:
  MOV SP, FP
  POP B, FP
  ADD SP, 1
  RET
sum:
  PUSH LR, B, C, FP
  SUB SP, 2
  MOV FP, SP
  MOV B, 0
  ST [FP, 0], B ; s
  MOV B, 0
  ST [FP, 1], B ; i
.L2:
  LD B, [FP, 1] ; i
  LD C, [FP, 6] ; n
  CMP B, C
  JGE .L4
  LD B, [FP, 0] ; s
  LD C, [FP, 1] ; i
  PUSH C
  LD C, [FP, 7] ; f
  CALL C
  MOV C, A
  ADD B, C
  ST [FP, 0], B ; s
.L3:
  LD B, [FP, 1] ; i
  ADD C, B, 1
  ST [FP, 1], C ; i
  JR .L2
.L4:
  LD B, [FP, 0] ; s
  JR .L1
.L1:
  MOV A, B
  MOV SP, FP
  ADD SP, 2
  POP LR, B, C, FP
  ADD SP, 2
  RET
main:
  PUSH LR, B, FP
  MOV FP, SP
  LDW B, =sqr
  PUSH B
  MOV B, 5
  PUSH B
  CALL sum
  MOV B, A
  JR .L5
.L5:
  MOV A, B
  MOV SP, FP
  POP LR, B, FP
  RET