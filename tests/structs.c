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
    struct Cat* c;
    c = &cat;
    cat.age = 10;
    cat.name = "Cloud";
    cat.owner.name = "Colin";
    cat.owner.email = "ccslon@gmail.com";
    int* ptr = &cat.age;
    char* cat_name = cat.name;

    
    c->age = 5;
}

void bar() {
    struct Cat* c;
    c = 0xcccc;
    c->age = 5;
}