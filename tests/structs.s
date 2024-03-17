.S0: "Cloud\0"
.S1: "Colin\0"
.S2: "ccslon@gmail.com\0"
.S3: "ccs@email.com\0"
.S4: "Nick\0"
.S5: "nickel@email.com\0"
.S6: "Nicole\0"
stack_cat:
  PUSH A, B, FP
  SUB SP, 6
  MOV FP, SP
  MOV A, 10
  ADD B, FP, 0
  LD [B, 1], A ; age
  LD A, =.S0
  ADD B, FP, 0
  LD [B, 0], A ; name
  LD A, =.S1
  ADD B, FP, 0
  ADD B, 2
  LD [B, 0], A ; name
  LD A, =.S2
  ADD B, FP, 0
  ADD B, 2
  LD [B, 1], A ; email
  ADD A, FP, 0
  LD A, [A, 1] ; age
  LD [FP, 4], A ; age
  ADD A, FP, 0
  ADD A, 2
  LD A, [A, 0] ; name
  LD [FP, 5], A ; name
  MOV SP, FP
  ADD SP, 6
  POP A, B, FP
  RET
init_cat:
  PUSH A, B, FP
  SUB SP, 6
  MOV FP, SP
  ADD A, FP, 0
  LD B, =.S1
  LD [A, 0], B
  LD B, =.S3
  LD [A, 1], B
  ADD A, FP, 2
  LD B, [FP, 9] ; name
  LD [A, 0], B
  MOV B, 10
  LD [A, 1], B
  LD B, =.S1
  LD [A, 2], B
  LD B, =.S3
  LD [A, 3], B
  MOV SP, FP
  ADD SP, 6
  POP A, B, FP
  ADD SP, 1
  RET
array:
  PUSH A, B, C, FP
  SUB SP, 5
  MOV FP, SP
  ADD A, FP, 0
  LD B, =.S1
  LD [A, 0], B
  LD B, =.S3
  LD [A, 1], B
  LD B, =.S4
  LD [A, 2], B
  LD B, =.S5
  LD [A, 3], B
  ADD A, FP, 0
  MOV B, 0
  MUL B, 2
  ADD A, B
  LD A, [A, 0] ; name
  LD [FP, 4], A ; name
  LD A, =.S6
  ADD B, FP, 0
  MOV C, 1
  MUL C, 2
  ADD B, C
  LD [B, 0], A ; name
  MOV SP, FP
  ADD SP, 5
  POP A, B, C, FP
  RET