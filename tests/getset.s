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
  LD [B], A
  MOV SP, FP
  POP A, B, C, FP
  ADD SP, 3
  RET