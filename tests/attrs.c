struct Owner {
    char* name;
    int phone;
};
struct Cat {
    char* name;
    int age;
    struct Owner* owner;
};

void test2() {
    struct Owner me;
    me.name = "Colin";
    me.phone = 1000;
    char* bar = me.name;
}