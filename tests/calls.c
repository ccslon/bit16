int baz(int y, int z) {
    return y*z;
}

int bar(int x, int y) {
    return x*y;
}

int foo(int x, int y, int z) {
    return bar(x, y) + baz(y, z);
}