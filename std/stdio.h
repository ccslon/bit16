
struct FILE {
    int* buffer;
    int read;
    int write;
};
struct FILE* stdout = {0x7f00, 0, 0};

int putchar(char c) {
    fputc(c, stdout);
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
int fputc(char c, struct FILE* stream) {
    stream->buffer[stream->write++] = c;
    return 0;
}