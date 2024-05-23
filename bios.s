OUT_ADDR = 0x8000
MOV A, 1
MOV B, 2
PUSH A
PUSH B
POP C
POP D

main:
    MOV SP, 0x0700
    LD B, =msg
loop:
    LD A, [B]
    CMP A, '\0'
    JEQ done
    PUSH A
    CALL output
    ADD B, 1
    JR loop
done:
    HALT
output:
    PUSH B
    LD B, =OUT_ADDR
    LD A, [SP, 1]
    LD [B], A
    POP B
    RET
msg: "Hello world!\n\0"
