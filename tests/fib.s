fib:
  PUSH LR, B, C, FP
  MOV FP, SP
  LD B, [FP, 4] ; n
  CMP B, 1
  JNE .L2
  MOV B, 0
  JR .L0
.L2:
  LD B, [FP, 4] ; n
  CMP B, 2
  JNE .L3
  MOV B, 1
  JR .L0
.L3:
  LD B, [FP, 4] ; n
  SUB B, 1
  PUSH B
  CALL fib
  MOV B, A
  LD C, [FP, 4] ; n
  SUB C, 2
  PUSH C
  CALL fib
  MOV C, A
  ADD B, C
  JR .L0
.L0:
  MOV A, B
  MOV SP, FP
  POP LR, B, C, FP
  ADD SP, 1
  RET
fib2:
  PUSH LR, B, C, FP
  MOV FP, SP
  LD B, [FP, 4] ; n
  CMP B, 1
  JEQ .L7
  CMP B, 2
  JEQ .L8
  JR .L9
.L7:
  MOV B, 0
  JR .L4
.L8:
  MOV B, 1
  JR .L4
.L9:
  LD B, [FP, 4] ; n
  SUB B, 1
  PUSH B
  CALL fib
  MOV B, A
  LD C, [FP, 4] ; n
  SUB C, 2
  PUSH C
  CALL fib
  MOV C, A
  ADD B, C
  JR .L4
.L6:
.L4:
  MOV A, B
  MOV SP, FP
  POP LR, B, C, FP
  ADD SP, 1
  RET