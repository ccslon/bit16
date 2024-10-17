div:
  PUSH B, FP
  SUB SP, 2
  MOV FP, SP
  MOV A, 3
  ADD B, FP, 0
  ST [B, 0], A ; quot
  MOV A, 4
  ADD B, FP, 0
  ST [B, 1], A ; rem
  ADD A, FP, 0
  JR .L0
.L0:
  MOV SP, FP
  ADD SP, 2
  POP B, FP
  ADD SP, 2
  RET
print_int:
  PUSH LR, A, B, C, D, FP
  SUB SP, 2
  MOV FP, SP
  MOV B, 10
  PUSH B
  LD B, [FP, 8] ; num
  PUSH B
  CALL div
  MOV B, A
  ADD C, FP, 0
  LD D, [B, 0]
  ST [C, 0], D
  LD D, [B, 1]
  ST [C, 1], D
  MOV SP, FP
  ADD SP, 2
  POP LR, A, B, C, D, FP
  ADD SP, 1
  RET