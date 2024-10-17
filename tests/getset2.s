array: space 100
get2:
  PUSH B, FP
  MOV FP, SP
  LD A, [FP, 2] ; g
  LD B, [FP, 3] ; i
  ADD A, B
  LD A, [A]
  LD B, [FP, 4] ; j
  ADD A, B
  LD A, [A]
  JR .L0
.L0:
  MOV SP, FP
  POP B, FP
  ADD SP, 3
  RET
set2:
  PUSH A, B, C, FP
  MOV FP, SP
  LD A, [FP, 7] ; t
  LD B, [FP, 4] ; g
  LD C, [FP, 5] ; i
  ADD B, C
  LD B, [B]
  LD C, [FP, 6] ; j
  ADD B, C
  ST [B], A
  MOV SP, FP
  POP A, B, C, FP
  ADD SP, 4
  RET
getarray2:
  PUSH B, FP
  MOV FP, SP
  LDW A, =array
  LD B, [FP, 2] ; i
  MUL B, 10
  ADD A, B
  LD B, [FP, 3] ; j
  ADD A, B
  LD A, [A]
  JR .L1
.L1:
  MOV SP, FP
  POP B, FP
  ADD SP, 2
  RET
setarray2:
  PUSH A, B, C, FP
  MOV FP, SP
  LD A, [FP, 6] ; t
  LDW B, =array
  LD C, [FP, 4] ; i
  MUL C, 10
  ADD B, C
  LD C, [FP, 5] ; j
  ADD B, C
  ST [B], A
  MOV SP, FP
  POP A, B, C, FP
  ADD SP, 3
  RET
getstack:
  PUSH B, FP
  SUB SP, 25
  MOV FP, SP
  ADD A, FP, 0
  LD B, [FP, 27] ; i
  MUL B, 5
  ADD A, B
  LD B, [FP, 28] ; j
  ADD A, B
  LD A, [A]
  JR .L2
.L2:
  MOV SP, FP
  ADD SP, 25
  POP B, FP
  ADD SP, 2
  RET
getstack:
  PUSH B, C, FP
  SUB SP, 25
  MOV FP, SP
  LD A, [FP, 30] ; t
  ADD B, FP, 0
  LD C, [FP, 28] ; i
  MUL C, 5
  ADD B, C
  LD C, [FP, 29] ; j
  ADD B, C
  ST [B], A
.L3:
  MOV SP, FP
  ADD SP, 25
  POP B, C, FP
  ADD SP, 3
  RET