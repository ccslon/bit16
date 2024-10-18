change:
  PUSH A, B, FP
  MOV FP, SP
  LD A, [FP, 3] ; n
  LD A, [A]
  ADD A, 10
  LD B, [FP, 3] ; n
  ST [B], A
  MOV SP, FP
  POP A, B, FP
  ADD SP, 1
  RET
foo:
  PUSH LR, A, B, FP
  SUB SP, 1
  MOV FP, SP
  LD B, [FP, 5] ; m
  MUL B, 5
  ST [FP, 0], B ; n
  ADD B, FP, 0
  PUSH B
  CALL change
  MOV SP, FP
  ADD SP, 1
  POP LR, A, B, FP
  ADD SP, 1
  RET
print:
  PUSH FP
  MOV FP, SP
  MOV SP, FP
  POP FP
  ADD SP, 1
  RET
bar:
  PUSH LR, A, B, C, FP
  MOV FP, SP
  LD B, [FP, 5] ; str
  PUSH B
  CALL print
  LD B, [FP, 5] ; str
  LD C, [FP, 6] ; i
  ADD B, C
  PUSH B
  CALL print
  MOV SP, FP
  POP LR, A, B, C, FP
  ADD SP, 2
  RET