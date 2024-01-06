#define FILE struct _FILE_
struct _FILE_ {
    int* buffer;
    int read;
    int write;
};
FILE stdout = {0x7f00, 0, 0};
int fputc(char c, FILE* stream) {
    stream->buffer[stream->write++] = c;
    return 0;
}
int putchar(char c) {
    fputc(c, &stdout);
    return 0;
}
int fputs(const char* str, FILE* stream) {
    while (*str != '\0') {
        fputc(*str, stream);
        str++;
    }
    return 0;
}
int puts(const char* str) {
    fputs(str, &stdout);
    putchar('\n');
    return 0;
}
void printd(int n) {
    if (n < 0) {
        putchar('-');
        n = -n;
    }
    int div = 0;
    int mod = n;
    while (mod >= 10) { // "division"
        mod -= 10;
        div++;
    }
    if (div) 
        printd(div);
    putchar(mod + '0');
}
void printf(char* fmt, ...) {
    int* ap;
    (ap = _VARLIST_);
    char* c;
    for (c = fmt; *c; c++) {
        if (*c == '%') {
            switch (*++c) {
                case 'd': {
                    printd(((int)*ap++));
                    break;
                }
                case 's': {
                    fputs(((char*)*ap++), &stdout);
                    break;
                }
                default: putchar(*c);
            }
        } else {
            putchar(*c);
        }
    }
    (ap = 0);
}