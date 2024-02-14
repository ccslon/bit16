struct Idk {
    int a, *b;
} dunno;

void foo() {
    int *i = (int*)33;
    dunno.a = 44;
    dunno.b = (int*)55;
}