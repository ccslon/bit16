char* STDOUT = 0x7fff;
int putchar(char c) {
    *STDOUT = c;
    return 0;
}
int puts(char* str) {
    while (*str != '\0') {
        putchar(*str);
        str++;
    }
    return 0;
}