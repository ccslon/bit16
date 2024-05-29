struct Cat {
    char* name;
    int age;
    char* (*get_name)(struct Cat*);
};
char* get_name(struct Cat* cat) {
    return cat->name;
}
int sqr(int n) {
    return n * n;
}
int sum(int n, int (*f)(int)) {
    int s = 0, i;
    for (i = 0; i < n; i++) {
        s += (*f)(i);
    }
    return s;
}
int main() {
    struct Cat cat;
    cat.name = "Cloud";
    cat.age = 15;
    cat.get_name = &get_name;
    char* name = (*cat.get_name)(&cat);
    int n = sum(10, &sqr);
    return 0;
}