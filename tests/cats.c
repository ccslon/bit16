char* OUT = 0x7fff;
void put(char c) {
    *OUT = c;
}
void print(char* str) {
    while (*str != '\0') {
        put(*str);
        str++;
    }
}

struct Owner {
    char* name;
    char* email;
};

struct Cat {
    char* name;
    int age;
    struct Owner owner;
};

void main() {
    struct Cat cat;
    cat.name = "Cloud";

    print(cat.name);
    put('\n');
    print_ptr(&cat);
}

void print_ptr(struct Cat* cat) {
    cat->owner.name = "Colin";
    print(cat->owner.name);
}

