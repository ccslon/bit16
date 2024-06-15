void baz();
int foo(int a, int b) {
    do {
        baz();
    } while (a > b);
}