STACK_INIT = 0x8000
boot:
    NOP
    LDW SP, =STACK_INIT
    CALL main
    HALT