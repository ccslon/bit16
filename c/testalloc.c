//#include <stdlib.h>
void* malloc(int);
void free(void* ptr);
struct cat {
    char* name;
    int age;
};
typedef struct cat Cat;

void main() {
    Cat* cats = malloc(5 * sizeof(Cat));
    cats[0].name = "Cloud";
    cats[0].age = 15;
    free(cats);
}