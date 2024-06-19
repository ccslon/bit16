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
  LD B, =.S1
  LD [FP, 0], B ; ptr
  ADD B, FP, 1
  MOV C, 'H'
  LD [B, 0], C
  MOV C, 'e'
  LD [B, 1], C
  MOV C, 'l'
  LD [B, 2], C
  MOV C, 'l'
  LD [B, 3], C
  MOV C, 'o'
  LD [B, 4], C
  MOV C, ' '
  LD [B, 5], C
  MOV C, 's'
  LD [B, 6], C
  MOV C, 't'
  LD [B, 7], C
  MOV C, 'a'
  LD [B, 8], C
  MOV C, 'c'
  LD [B, 9], C
  MOV C, 'k'
  LD [B, 10], C
  MOV C, '['
  LD [B, 11], C
  MOV C, ']'
  LD [B, 12], C
  MOV C, '\n'
  LD [B, 13], C
  MOV C, '\0'
  LD [B, 14], C
  LD B, =.S2
  PUSH B
  CALL print
  LD B, =gptr
  LD B, [B]
  PUSH B
  CALL print
  LD B, =garr
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