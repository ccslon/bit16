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
    struct Cat* c;
    c = &cat;
    cat.age = 10;
    cat.name = "Cloud";
    cat.owner.name = "Colin";
    cat.owner.email = "ccslon@gmail.com";
    int* ptr = &cat.age;
    char* cat_name = cat.name;
    char* owner_name = cat.owner.name;

    c->age = 5;

}

void ptr_cat(struct Cat* cat) {

}

void array_cat() {
    struct Cat cats[3];
    struct Cat* cat2;    
    cat2 = &cats[2];
    
    int is[10];
    is[4] = 111;
}
