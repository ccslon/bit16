.S0: "Hello world!\n\0"
main:
  PUSH LR, B, FP
  MOV FP, SP
  LDW B, =.S0
  PUSH B
  CALL printf
  MOV B, 0
  JR .L0
.L0:
  MOV A, B
  MOV SP, FP
  POP LR, B, FP
  RET