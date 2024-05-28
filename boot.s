STACK_INIT = 0x8000
boot:
    NOP
    LD SP, =STACK_INIT
    CALL main
    HALT