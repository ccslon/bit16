struct Owner {
    char* name;
    char* email;
};

struct Cat {
    char* name;
    int age;
    struct Owner owner;
};

void foo() {
    struct Cat cat;
    cat.age = 10;
    cat.name = "Cloud";
    cat.owner.name = "Colin";
    cat.owner.email = "ccslon@gmail.com";
    int* ptr = &cat.age;
    char* cat_name = cat.name;

    struct Cat* c;
    c = &cat;
    c->age = 5;
}