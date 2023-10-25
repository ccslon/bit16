struct Owner {
    char* name;
    char* email;
};

struct Cat {
    char* name;
    int age;
    struct Owner owner;
};

void stack_cat() {
    struct Cat cat;
    cat.age = 10;
    cat.name = "Cloud";
    cat.owner.name = "Colin";
    cat.owner.email = "ccslon@gmail.com";
}