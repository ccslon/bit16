#define FILE struct _FILE_
struct _FILE_ {
    int* buffer;
    int read;
    int write;
};
FILE stdout = {(int*)0x7f00, 0, 0};
int fputc(char c, FILE* stream) {
    stream->buffer[stream->write] = c;
    stream->write++;
    return 0;
}
int putchar(char c) {
    return fputc(c, &stdout);
}
int fputs(const char* s, FILE* stream) {
    while (*s != '\0') {
        fputc(*s, stream);
        s++;
    }
    return 0;
}
int puts(const char* s) {
    fputs(s, &stdout);
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
    while (mod >= 10000) {
        mod -= 10000;
        div += 1000;
    }
    while (mod >= 1000) {
        mod -= 1000;
        div += 100;
    }
    while (mod >= 100) {
        mod -= 100;
        div += 10;
    }
    while (mod >= 10) { // "division"
        mod -= 10;
        div++;
    }
    if (div)
        printd(div);
    putchar(mod + '0');
}
void printf(const char* format, ...) {
    int* ap;
    (ap = (int*)&(format)+1);
    const char* c;
    for (c = format; *c; c++) {
        if (*c == '%') {
            switch (*++c) {
                case 'd': {
                    printd(((int)*ap++));
                    break;
                }
                case 's': {
                     printf(((char*)*ap++));
                    break;
                }
                case 'c': {
                    putchar(((char)*ap++));
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