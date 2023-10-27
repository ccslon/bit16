int foo(int bar) {
    if (bar > 3) {
        bar = 3;
        goto baz;
    }
    bar = bar * 3;
    baz:
    return bar;
}