.S0: "Hello global*\n\0"
gptr: .S0
garr:
  'H'
  'e'
  'l'
  'l'
  'o'
  ' '
  'g'
  'l'
  'o'
  'b'
  'a'
  'l'
  '['
  ']'
  '\n'
  '\0'
.S1: "Hello stack*\n\0"
.S2: "Hello cstrings!\n\0"
main:
  PUSH LR, B, C, FP
  SUB SP, 16
  MOV FP, SP
  LDW B, =.S1
  ST [FP, 0], B ; ptr
  ADD B, FP, 1
  MOV C, 'H'
  ST [B, 0], C
  MOV C, 'e'
  ST [B, 1], C
  MOV C, 'l'
  ST [B, 2], C
  MOV C, 'l'
  ST [B, 3], C
  MOV C, 'o'
  ST [B, 4], C
  MOV C, ' '
  ST [B, 5], C
  MOV C, 's'
  ST [B, 6], C
  MOV C, 't'
  ST [B, 7], C
  MOV C, 'a'
  ST [B, 8], C
  MOV C, 'c'
  ST [B, 9], C
  MOV C, 'k'
  ST [B, 10], C
  MOV C, '['
  ST [B, 11], C
  MOV C, ']'
  ST [B, 12], C
  MOV C, '\n'
  ST [B, 13], C
  MOV C, '\0'
  ST [B, 14], C
  LDW B, =.S2
  PUSH B
  CALL print
  LDW B, =gptr
  LD B, [B]
  PUSH B
  CALL print
  LDW B, =garr
  PUSH B
  CALL print
  LD B, [FP, 0] ; ptr
  PUSH B
  CALL print
  ADD B, FP, 1
  PUSH B
  CALL print
.L0:
  MOV A, B
  MOV SP, FP
  ADD SP, 16
  POP LR, B, C, FP
  RET