.S0: "Colin\0"
.S1: "Mom\0"
owners:
  .S0
  34
  .S1
  21
cats: space 9
.S2: "Cats Ya!\0"
name: .S2
num: 69
.S3: "Cloud\0"
print_cat:
  PUSH A, FP
  SUB SP, 5
  MOV FP, SP
  LDW A, =name
  LD A, [A]
  ST [FP, 0], A ; store
  LDW A, =num
  LD A, [A]
  ST [FP, 1], A ; n
  LD A, [FP, 7] ; cat
  LD A, [A, 0] ; name
  ST [FP, 2], A ; mycat
  LD A, [FP, 7] ; cat
  LD A, [A, 1] ; age
  ST [FP, 3], A ; age
  LD A, [FP, 7] ; cat
  LD A, [A, 2] ; owner
  LD A, [A, 0] ; name
  ST [FP, 4], A ; owner
  MOV SP, FP
  ADD SP, 5
  POP A, FP
  ADD SP, 1
  RET
main:
  PUSH LR, B, C, FP
  SUB SP, 1
  MOV FP, SP
  LDW B, =cats
  MOV C, 0
  MUL C, 3
  ADD B, C
  ST [FP, 0], B ; cat1
  LDW B, =.S3
  LD C, [FP, 0] ; cat1
  ST [C, 0], B ; name
  MOV B, 10
  LD C, [FP, 0] ; cat1
  ST [C, 1], B ; age
  LDW B, =owners
  MOV C, 0
  MUL C, 2
  ADD B, C
  LD C, [FP, 0] ; cat1
  ST [C, 2], B ; owner
  LD B, [FP, 0] ; cat1
  PUSH B
  CALL print_cat
  MOV B, 0
  JR .L0
.L0:
  MOV A, B
  MOV SP, FP
  ADD SP, 1
  POP LR, B, C, FP
  RET