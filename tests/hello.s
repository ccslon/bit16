.S0: "Hello world!\n\0"
main:
  MOV FP, SP
  LD B, =.S0
  PUSH B
  CALL printf
  MOV SP, FP
  HALT