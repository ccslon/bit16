struct FILE {
    void* buffer;
    
}

const char* STDOUT = 0x7fff;
int putchar(char c) {
    *STDOUT = c;
    return 0;
}
int puts(const char* str) {
    while (*str != '\0') {
        putchar(*str);
        str++;
    }
    putchar('\n');
    return 0;
}