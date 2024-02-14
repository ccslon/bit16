struct Idk {
    int a, *b;
} dunno;

int num() {
    return 9;
}

int* alloc() {
    return (int*)0x3400;
}

struct Idk make_Idk() {
    struct Idk ret;
    return ret;
}

void print_Idk(struct Idk*);

void main() {
    int a = num();
    int b = a * num();
    int c = num() * num();
    int d = num() * c;
    int *e = alloc();
    struct Idk idk = make_Idk();
    idk.a = num();
    print_Idk(&idk);
}