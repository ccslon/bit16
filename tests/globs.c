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
Owner owners[2] = {{"Colin",34}, {"Mom", 21}};
Cat cats[3];
char* name = "Cats Ya!";
int num = 69;
void print_cat(Cat* cat) {
    char* store = name;
    int n = num;
    char* mycat = cat->name;    
    int age = cat->age;
    char* owner = cat->owner->name;
}
void main() {
    Cat* cat1 = &cats[0];
    cat1->name = "Cloud";
    cat1->age = 10;
    cat1->owner = &owners[0];
    print_cat(cat1);
}