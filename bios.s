STACK_INIT = 0x8000
OUT_ADDR = 0x8001
IN_ADDR = 0x8002
boot:
    NOP
    LD SP, =STACK_INIT
    JR main
input:
    PUSH B
    LD B, =IN_ADDR
    LD A, [B]
    POP B
    RET
output:
    PUSH B
    LD B, =OUT_ADDR
    LD A, [SP, 1]
    LD [B], A
    POP B
    ADD SP, 1
    RET