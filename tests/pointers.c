void change(int* n) {
    *n += 10;
}
void foo(int m) {
    int n = m * 5;
    change(&n);
}
void print(char* str) {

}
void bar(char* str, int i) {
    print(str);
    print(&str[i]);
}