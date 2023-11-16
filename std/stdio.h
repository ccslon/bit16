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