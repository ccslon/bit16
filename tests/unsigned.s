foo:
  PUSH B, FP
  SUB SP, 6
  MOV FP, SP
  LD A, [FP, 8] ; u
  LD B, [FP, 9] ; i
  CMP A, B
  JEQ .L1
  MOV A, 0
  JR .L2
.L1:
  MOV A, 1
.L2:
  LD [FP, 0], A ; a
  LD A, [FP, 8] ; u
  LD B, [FP, 9] ; i
  CMP A, B
  JNE .L3
  MOV A, 0
  JR .L4
.L3:
  MOV A, 1
.L4:
  LD [FP, 1], A ; b
  LD A, [FP, 8] ; u
  LD B, [FP, 9] ; i
  CMP A, B
  JHI .L5
  MOV A, 0
  JR .L6
.L5:
  MOV A, 1
.L6:
  LD [FP, 2], A ; c
  LD A, [FP, 8] ; u
  LD B, [FP, 9] ; i
  CMP A, B
  JCC .L7
  MOV A, 0
  JR .L8
.L7:
  MOV A, 1
.L8:
  LD [FP, 3], A ; d
  LD A, [FP, 8] ; u
  LD B, [FP, 9] ; i
  CMP A, B
  JCS .L9
  MOV A, 0
  JR .L10
.L9:
  MOV A, 1
.L10:
  LD [FP, 4], A ; e
  LD A, [FP, 8] ; u
  LD B, [FP, 9] ; i
  CMP A, B
  JLS .L11
  MOV A, 0
  JR .L12
.L11:
  MOV A, 1
.L12:
  LD [FP, 5], A ; f
.L0:
  MOV SP, FP
  ADD SP, 6
  POP B, FP
  ADD SP, 2
  RET