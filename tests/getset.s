array: space 10
get:
  PUSH B, FP
  MOV FP, SP
  LD A, [FP, 2] ; g
  LD B, [FP, 3] ; i
  ADD A, B
  LD A, [A]
  JR .L0
.L0:
  MOV SP, FP
  POP B, FP
  ADD SP, 2
  RET
set:
  PUSH A, B, C, FP
  MOV FP, SP
  LD A, [FP, 6] ; t
  LD B, [FP, 4] ; g
  LD C, [FP, 5] ; i
  ADD B, C
  ST [B], A
  MOV SP, FP
  POP A, B, C, FP
  ADD SP, 3
  RET
getarray:
  PUSH B, FP
  MOV FP, SP
  LDW A, =array
  LD B, [FP, 2] ; i
  ADD A, B
  LD A, [A]
  JR .L1
.L1:
  MOV SP, FP
  POP B, FP
  ADD SP, 1
  RET
setarray:
  PUSH A, B, C, FP
  MOV FP, SP
  LD A, [FP, 5] ; t
  LDW B, =array
  LD C, [FP, 4] ; i
  ADD B, C
  ST [B], A
  MOV SP, FP
  POP A, B, C, FP
  ADD SP, 2
  RET
getstack:
  PUSH B, FP
  SUB SP, 10
  MOV FP, SP
  ADD A, FP, 0
  LD B, [FP, 12] ; i
  ADD A, B
  LD A, [A]
  JR .L2
.L2:
  MOV SP, FP
  ADD SP, 10
  POP B, FP
  ADD SP, 1
  RET
getstack:
  PUSH B, C, FP
  SUB SP, 10
  MOV FP, SP
  LD A, [FP, 14] ; t
  ADD B, FP, 0
  LD C, [FP, 13] ; i
  ADD B, C
  ST [B], A
.L3:
  MOV SP, FP
  ADD SP, 10
  POP B, C, FP
  ADD SP, 2
  RET