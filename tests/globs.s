.S0: "Cloud\0"
.S1: "Colin\0"
.S2: "Mom\0"
owners:
  .S1
  34
  .S2
  21
cats: space 9
name: "Cats Ya!\0"
num: 69
main:
  SUB SP, 1
  MOV FP, SP
  LD B, =cats
  MOV C, 0
  MUL C, 3
  ADD B, C
  LD [FP, 0], B ; cat1
  LD B, =.S0
  LD C, [FP, 0] ; cat1
  LD [C, 0], B ; name
  MOV B, 10
  LD C, [FP, 0] ; cat1
  LD [C, 1], B ; age
  LD B, =owners
  MOV C, 0
  MUL C, 2
  ADD B, C
  LD C, [FP, 0] ; cat1
  LD [C, 2], B ; owner
  LD B, [FP, 0] ; cat1
  PUSH B
  CALL print_cat
  MOV SP, FP
  ADD SP, 1
  HALT
print_cat:
  PUSH A, FP
  SUB SP, 5
  MOV FP, SP
  LD A, =name
  LD [FP, 0], A ; store
  LD A, =num
  LD A, [A]
  LD [FP, 1], A ; n
  LD A, [FP, 7] ; cat
  LD A, [A, 0] ; name
  LD [FP, 2], A ; mycat
  LD A, [FP, 7] ; cat
  LD A, [A, 1] ; age
  LD [FP, 3], A ; age
  LD A, [FP, 7] ; cat
  LD A, [A, 2] ; owner
  LD A, [A, 0] ; name
  LD [FP, 4], A ; owner
  MOV SP, FP
  ADD SP, 5
  POP A, FP
  ADD SP, 1
  RET