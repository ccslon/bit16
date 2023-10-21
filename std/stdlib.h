int div(int num, int den) {
    int quot = 0;
    while (num >= den) {
        num -= den;
        quot++;
    }
    return quot;
}
int mod(int num, int den) {
    while (num >= den) num -= d;
    return num;
}
int not(int num) {
    return num == 0;
}
int abs(int num) {
    if (num < 0) return -num;
    return num;
}
int rand() {

}
int srand(int seed) {
    
}
#include <string.h>
int atoi(char* str) {
    str = strrev(str);
    int place = 1;
    int num = 0;
    while (*str != '\0') {
        num += place * (*str - '0');
        place *= 10;
        str++;
    }
    return num;
}
void* calloc(int nitems, int size) {

}
void free(void* ptr) {

}
void* malloc(int size) {

}
void* realloc(void* ptr, int size) {

}