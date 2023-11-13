struct FILE {
    char* buffer;
    int read;
    int write;
};
struct FILE stdout;
struct FILE stdin = {0x7e00, 0, 0};
void main() {
    stdout.buffer = 0x7f00;
    stdout.read = 0;
    stdout.write = 0;
    int head = stdin.read;
}
