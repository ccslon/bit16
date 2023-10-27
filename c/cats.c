#include <stdio.h>
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
    struct Owner me = {"Colin", "ccs@email.com"};
    puts(me.name);
    puts(me.email);
    char* honey = "Honey";
    struct Cat cat = {honey,10,{"Nick", "Nickel@email.com"}};
    puts(cat.name);
    puts(cat.owner.name);
    puts(cat.owner.email);
    struct Cat cats[2];
    cats[0].name = "Sam";
    cats[1].name = "Pippin";
    int i;
    for (i = 0; i < 2; i++) {
        puts(cats[i].name);
    }    
}