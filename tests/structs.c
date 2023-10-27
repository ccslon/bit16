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
    int age = cat.age;
    char* name = cat.owner.name;
}

void init_cat(char* name) {
    struct Owner owner = {"Colin", "ccs@email.com"};
    struct Cat cat = {name,10,{"Colin", "ccs@email.com"}};
}

void array() {    
    struct Owner owners[2] = {{"Colin", "ccs@email.com"}, {"Nick", "nickel@email.com"}};
    char* name = owners[0].name;
    owners[1].name = "Nicole";
}