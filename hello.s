.S0: "Hello world! "
  LD B, =.S0
  MOV A, B
  CALL print
  MOV B, A
  HALT
OUT: 32767
put:
  SUB SP, 1
  LD [SP, 0], A
  LD A, [SP, 0]
  LD B, =OUT
  LD B, [B]
  LD [B], A
  ADD SP, 1
  RET
print:
  PUSH LR, B
  SUB SP, 1
  LD [SP, 0], A
.L0:
  LD B, [SP, 0]
  LD B, [B]
  LD C, '\0'
  CMP B, C
  JEQ .L1
  LD B, [SP, 0]
  LD B, [B]
  MOV A, B
  CALL put
  MOV B, A
  LD B, [SP, 0]
  ADD B, 1
  LD [SP, 0], B
  JR .L0
.L1:
  ADD SP, 1
  POP PC, B