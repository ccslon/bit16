void print(char*);
char* gptr = "Hello global*\n";
char garr[16] = "Hello global[]\n";

int main() {
    char* ptr = "Hello stack*\n";
    char arr[] = "Hello stack[]\n";
    print("Hello cstrings!\n");
    print(gptr);
    print(garr);
    print(ptr);
    print(arr);
}