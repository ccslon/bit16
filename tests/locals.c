void locals() {
    int foo;
    int bar = 9;
    foo = 8;
    int baz = foo + -bar;
    {
     char foo;
     foo = 'g';
    }
    foo = 5;
    const int* ptr = 6;
}