#include <stdio.h>
#include <stdlib.h>
typedef struct _Owner_ {
    char* name;
    int phone;
} Owner;
typedef struct _Cat_ {
    char* name;
    int age;
    Owner* owner;
} Cat;
int dofib(const int n, const int a, const int b) {
    switch (n) {
        case 1: return a;
        case 2: return b;
        default: {
            return dofib(n-1, b, a+b);
        }
    }
}
int fib(const int n) {
    return dofib(n, 0, 1);
}

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
int intcmp(int a, int b) {
    return a - b;
}
#define LEN 5
int arr[LEN];
#define N 7
int sarr[6] = {1,2,3,4,4,6};
void main() {
    //Hello
    printf("Hello world!\n");
    //Fib
    int i;
    printf("Fib! %d %d\n", 0, 1);
    for (i = 1; i <= 10; i++)
        printf("%d\n", fib(i));  
    //Cats
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
    //sort
    for (i = 0; i < LEN; i++)
        arr[i] = rand();
    for (i = 0; i < LEN; i++)
        printf("%d ", arr[i]);
    putchar('\n');
    qsort(arr, 0, LEN-1, &intcmp);
    for (i = 0; i < LEN; i++)
        printf("%d ", arr[i]);
    putchar('\n');
    //bsearch
    for (i = 0; i < N; i++) {
        printf("%d\n", bsearch(i, sarr, 6, &intcmp));
    }
}
