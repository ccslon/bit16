#define NULL (void*)0
#define INPORT 0x8000
#define INBUFFER 0x7e00
typedef struct _FILE_ {
    char* buffer;
    int read;
    int write;
} FILE;
FILE stdin = {(char*)0x0, 0, 0};
FILE stdout = {(char*)0x8000, 0, 0};
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
    while (--n > 0 && (c = fgetc(stream))) // "enter"
        if ((*cs++ = c) == '\n')
            break;
    *cs = '\0';
    return s;
}
char* gets(char* s) {
    return fgets(s, 0xff, &stdin);
}
int fputc(char c, FILE* stream) {
    *stream->buffer = c;
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
    if (n / 10)
        printd(n / 10);
    putchar(n % 10 + '0');
}
void printx(int n, char uplo) {
    if (n < 0) {
        putchar('-');
        n = -n;
    }
    if (n / 16)
        printx(n / 16, uplo);
    if (n % 16 > 9) 
        putchar(n % 16 - 10 + uplo);
    else
        putchar(n % 16 + '0');
}
void printf(const char* format, ...) {
    int* ap;
    (ap = (int*)&(format)+1);
    const char* c;
    for (c = format; *c; c++) {
        if (*c == '%') {
            switch (*++c) {
                case 'i': ;
                case 'd': {
                    printd(((int)*ap++));
                    break;
                }
                case 'x': {
                    printx(((int)*ap++), 'a');
                    break;
                }
                case 'X': {
                    printx(((int)*ap++), 'A');
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
    (ap = (int*)0);
}