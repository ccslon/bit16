fact:
  PUSH LR, B, C, FP
  MOV FP, SP
  LD B, [FP, 4] ; n
  CMP B, 0
  JNE .L1
  MOV B, 1
  JR .L0
.L1:
  LD B, [FP, 4] ; n
  LD C, [FP, 4] ; n
  SUB C, 1
  PUSH C
  CALL fact
  MOV C, A
  MUL B, C
  JR .L0
.L0:
  MOV A, B
  MOV SP, FP
  POP LR, B, C, FP
  ADD SP, 1
  RET