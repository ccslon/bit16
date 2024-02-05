#define FILE struct _FILE_
struct _FILE_ {
    char* buffer;
    int read;
    int write;
};
FILE stdin = {(char*)0x7e00, 0, 0};
FILE stdout = {(char*)0x7f00, 0, 0};
char fgetc(FILE* stream) {
    return stream->buffer[stream->read++];
}
#define getc() (fgetc(&stdin))
char getchar() {
    return fgetc(&stdin);
}
char* fgets(char* s, int n, FILE* stream) {
    char c;
    char* cs = s;
    while (--n > 0 && (c = getc(stream))) // "enter"
        if ((*cs++ = c) == '\n')
            break;
    *cs = '\0';
    return (c && c == c) ? 0 : s;
}
char* gets(char* s) {

}
int fputc(char c, FILE* stream) {
    stream->buffer[stream->write] = c;
    stream->write++;
    return 0;
}
#define putc(c) (fputc(c, &stdout))
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
void printx(int n) {
    if (n < 0) {
        putchar('-');
        n = -n;
    }
    int div = 0;
    int mod = n;
    while (mod >= 4096) { //16^3
        mod -= 4096;
        div += 256;
    }
    while (mod >= 256) { //16^2
        mod -= 256;
        div += 16;
    }
    while (mod >= 16) { //16^1
        mod -= 16;
        div++;
    }
    if (div)
        printx(div);
    if (mod > 9) 
        putchar(mod - 10 + 'a');
    else
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
                case 'x': {
                    printx(((int)*ap++));
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