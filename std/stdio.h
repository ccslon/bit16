#define NULL (void*)0
typedef unsigned int size_t;
typedef int* FILE;
FILE stdout = (FILE)0x8000;
FILE stdin = (FILE)0x8001;
char fgetc(FILE* stream) {
    return **stream;
}
#define getc() (fgetc(&stdin))
char getchar() {
    return *stdin;
}
char* fgets(char* s, size_t n, FILE* stream) {
    char c;
    char* cs = s;
    while (--n > 0 && (c = fgetc(stream))) // "enter"
        if ((*cs++ = c) == '\n')
            break;
    *cs = '\0';
    return s;
}
char* gets(char* s) {
    return fgets(s, 0xffff, &stdin);
}
int fputc(char c, FILE* stream) {
    **stream = c;
    return 0;
}
#define putc(c) (fputc(c, &stdout))
int putchar(char c) {
    *stdout = c;
    return 0;
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
void printu(unsigned int n) {
    if (n / 10)
        printu(n / 10);
    putchar(n % 10 + '0');
}
void printd(int n) {
    if (n < 0) {
        putchar('-');
        n = -n;
    }
    printu(n);
}
void printx(unsigned int n, char uplo) {
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
                case 'u': {
                    printu(((unsigned int)*ap++));
                    break;
                }
                case 'i': ;
                case 'd': {
                    printd(((int)*ap++));
                    break;
                }
                case 'x': {
                    printx(((unsigned int)*ap++), 'a');
                    break;
                }
                case 'X': {
                    printx(((unsigned int)*ap++), 'A');
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