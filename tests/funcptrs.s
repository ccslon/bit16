.S0: "Cloud\0"
get_name:
  PUSH FP
  MOV FP, SP
  LD A, [FP, 1] ; cat
  LD A, [A, 0] ; name
  JR .L0
.L0:
  MOV SP, FP
  POP FP
  ADD SP, 1
  RET
sqr:
  PUSH B, FP
  MOV FP, SP
  LD A, [FP, 2] ; n
  LD B, [FP, 2] ; n
  MUL A, B
  JR .L1
.L1:
  MOV SP, FP
  POP B, FP
  ADD SP, 1
  RET
sum:
  PUSH LR, B, C, FP
  SUB SP, 2
  MOV FP, SP
  MOV B, 0
  LD [FP, 0], B ; s
  MOV B, 0
  LD [FP, 1], B ; i
.L3:
  LD B, [FP, 1] ; i
  LD C, [FP, 6] ; n
  CMP B, C
  JGE .L5
  LD B, [FP, 0] ; s
  LD C, [FP, 1] ; i
  PUSH C
  LD C, [FP, 7] ; f
  CALL C
  MOV C, A
  ADD B, C
  LD [FP, 0], B ; s
.L4:
  LD B, [FP, 1] ; i
  ADD C, B, 1
  LD [FP, 1], C ; i
  JR .L3
.L5:
  LD B, [FP, 0] ; s
  JR .L2
.L2:
  MOV A, B
  MOV SP, FP
  ADD SP, 2
  POP LR, B, C, FP
  ADD SP, 2
  RET
main:
  SUB SP, 5
  MOV FP, SP
  LD B, =.S0
  ADD C, FP, 0
  LD [C, 0], B ; name
  MOV B, 15
  ADD C, FP, 0
  LD [C, 1], B ; age
  LD B, =get_name
  ADD C, FP, 0
  LD [C, 2], B ; get_name
  ADD B, FP, 0
  PUSH B
  ADD B, FP, 0
  LD B, [B, 2] ; get_name
  CALL B
  MOV B, A
  LD [FP, 3], B ; name
  LD B, =sqr
  PUSH B
  MOV B, 10
  PUSH B
  CALL sum
  MOV B, A
  LD [FP, 4], B ; n
  MOV SP, FP
  ADD SP, 5
  HALT