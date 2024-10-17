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
  ST [FP, 0], B ; n
.L3:
  CALL baz
  LD B, [FP, 4] ; a
  CMP B, 0
  JEQ .L5
  LD B, [FP, 5] ; b
  CMP B, 0
  JNE .L3
.L5:
.L4:
  LD B, [FP, 4] ; a
  CMP B, 0
  JEQ .L6
  LD B, [FP, 5] ; b
  CMP B, 0
  JEQ .L6
  MOV B, 100
  JR .L0
.L6:
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
  JNE .L8
  LD B, [FP, 5] ; b
  CMP B, 0
  JEQ .L9
.L8:
  MOV B, 1
  JR .L10
.L9:
  MOV B, 0
.L10:
  ST [FP, 0], B ; n
.L11:
  CALL baz
  LD B, [FP, 4] ; a
  CMP B, 0
  JNE .L11
  LD B, [FP, 5] ; b
  CMP B, 0
  JNE .L11
.L12:
  LD B, [FP, 4] ; a
  CMP B, 0
  JNE .L14
  LD B, [FP, 5] ; b
  CMP B, 0
  JEQ .L13
.L14:
  MOV B, 100
  JR .L7
.L13:
.L7:
  MOV A, B
  MOV SP, FP
  ADD SP, 1
  POP LR, B, FP
  ADD SP, 2
  RET