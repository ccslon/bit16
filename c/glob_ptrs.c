void printf(char*, ...);

int* gg = (int*)0x4567;

void print(char*);
char* msg = "hi";

int main() {
    print("Hello");
}

void a() {
    printf("%d\n", gg);
}

void b() {
    char str[3] = "yo";
    printf("%s\n", str);
}

void c() {
    char *str = "hi";
    printf("%s\n", str);
}

void d() {
    printf("%s\n", msg);
}