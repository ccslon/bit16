#include <stdio.h>
#define Cat struct _Cat_
#define Owner struct _Owner_
Owner {
    char* name;
    int phone;
}; 

Cat {
    char* name;
    int age;
    Owner* owner;
};

Owner owners[3] = {{"Colin",34}, {"Mom", 21},{"Nick", 524}};
Cat cats[3];
char* name = "Cats Ya!";
int num = 69;

void print_cat(Cat* cat) {    
    printf("%s %d\n", cat->name, cat->age);
    printf("%s\n", cat->owner->name);
}
Cat make_cat(char* name, int age, Owner* owner) {
    Cat cat;
    cat.name = name;
    cat.age = age;
    cat.owner = owner;
    return cat;
}
void main() {
    printf("%s\n", name);
    printd(num);
    putchar('\n');
    Cat* cat1 = &cats[0];
    cat1->name = "Cloud";
    cat1->age = 10;
    cat1->owner = &owners[0];
    print_cat(cat1);
    Cat cat2;
    cat2 = make_cat("Chuck",15,&owners[2]);
    print_cat(&cat2);
}