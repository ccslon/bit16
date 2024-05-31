foo:
  PUSH LR, B, FP
  SUB SP, 1
  MOV FP, SP
  LD B, [FP, 4] ; a
  CMP B, 0
  JEQ .L1
  LD B, [FP, 5] ; b
  CMP B, 0
  JEQ .L1
  MOV B, 1
  JR .L2
.L1:
  MOV B, 0
.L2:
  LD [FP, 0], B ; n
.L3:
  CALL baz
  LD B, [FP, 4] ; a
  CMP B, 0
  JEQ .L4
  LD B, [FP, 5] ; b
  CMP B, 0
  JNE .L3
.L4:
  LD B, [FP, 4] ; a
  CMP B, 0
  JEQ .L5
  LD B, [FP, 5] ; b
  CMP B, 0
  JEQ .L5
  MOV B, 100
  JR .L0
.L5:
.L0:
  MOV A, B
  MOV SP, FP
  ADD SP, 1
  POP LR, B, FP
  ADD SP, 2
  RET
bar:
  PUSH LR, B, FP
  SUB SP, 1
  MOV FP, SP
  LD B, [FP, 4] ; a
  CMP B, 0
  JNE .L7
  LD B, [FP, 5] ; b
  CMP B, 0
  JEQ .L8
.L7:
  MOV B, 1
  JR .L9
.L8:
  MOV B, 0
.L9:
  LD [FP, 0], B ; n
.L10:
  CALL baz
  LD B, [FP, 4] ; a
  CMP B, 0
  JNE .L10
  LD B, [FP, 5] ; b
  CMP B, 0
  JNE .L10
.L11:
  LD B, [FP, 4] ; a
  CMP B, 0
  JNE .L13
  LD B, [FP, 5] ; b
  CMP B, 0
  JEQ .L12
.L13:
  MOV B, 100
  JR .L6
.L12:
.L6:
  MOV A, B
  MOV SP, FP
  ADD SP, 1
  POP LR, B, FP
  ADD SP, 2
  RET