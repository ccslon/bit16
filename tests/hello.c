int OUT = 0x7fff;

void put(char c) {
    *OUT = c;
}
void print(char *str) {
    while (*str != '\0') {
        put(*str);
        str++;
    }
}
void main() {
    print("Hello world!");
}