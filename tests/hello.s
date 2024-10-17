.S0: "Hello world!\n\0"
main:
  PUSH LR, A, B, FP
  MOV FP, SP
  LDW B, =.S0
  PUSH B
  CALL printf
  MOV SP, FP
  POP LR, A, B, FP
  RET