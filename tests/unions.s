.S0: "(STR, %s)\0"
.S1: "(NUM, %d)\0"
.S2: "Hello!\0"
intToken:
  PUSH B, FP
  SUB SP, 2
  MOV FP, SP
  MOV A, 1
  ADD B, FP, 0
  LD [B, 0], A ; type
  LD A, [FP, 4] ; num
  ADD B, FP, 0
  ADD B, 1
  LD [B, 0], A ; num
  ADD A, FP, 0
  JR .L0
.L0:
  MOV SP, FP
  ADD SP, 2
  POP B, FP
  ADD SP, 1
  RET
strToken:
  PUSH B, FP
  SUB SP, 2
  MOV FP, SP
  MOV A, 0
  ADD B, FP, 0
  LD [B, 0], A ; type
  LD A, [FP, 4] ; str
  ADD B, FP, 0
  ADD B, 1
  LD [B, 0], A ; str
  ADD A, FP, 0
  JR .L1
.L1:
  MOV SP, FP
  ADD SP, 2
  POP B, FP
  ADD SP, 1
  RET
printToken:
  PUSH LR, A, B, FP
  MOV FP, SP
  LD B, [FP, 4] ; token
  LD B, [B, 0] ; type
  CMP B, 0
  JEQ .L4
  CMP B, 1
  JEQ .L5
  JR .L3
.L4:
  LD B, [FP, 4] ; token
  ADD B, 1
  LD B, [B, 0] ; str
  PUSH B
  LD B, =.S0
  PUSH B
  CALL printf
  ADD SP, 1
  JR .L3
.L5:
  LD B, [FP, 4] ; token
  ADD B, 1
  LD B, [B, 0] ; num
  PUSH B
  LD B, =.S1
  PUSH B
  CALL printf
  ADD SP, 1
  JR .L3
.L3:
  MOV SP, FP
  POP LR, A, B, FP
  ADD SP, 1
  RET
main:
  PUSH LR, B, C, D, FP
  SUB SP, 4
  MOV FP, SP
  MOV B, 5
  PUSH B
  CALL intToken
  MOV B, A
  ADD C, FP, 0
  LD D, [B, 0]
  LD [C, 0], D
  LD D, [B, 1]
  LD [C, 1], D
  ADD B, FP, 0
  PUSH B
  CALL printToken
  LD B, =.S2
  PUSH B
  CALL strToken
  MOV B, A
  ADD C, FP, 2
  LD D, [B, 0]
  LD [C, 0], D
  LD D, [B, 1]
  LD [C, 1], D
  ADD B, FP, 2
  PUSH B
  CALL printToken
.L6:
  MOV A, B
  MOV SP, FP
  ADD SP, 4
  POP LR, B, C, D, FP
  RET