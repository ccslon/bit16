typedef unsigned int size_t;
size_t strlen(const char* s) {
    size_t l = 0;
    while (s[l] != '\0')
        l++;
    return l;
}
char* strcpy(char* s, const char* t) {
    size_t i;
    for (i = 0; (s[i] = t[i]) != '\0'; i++) 
        ;
    return s;
}
char* strncpy(char* s, const char* t, size_t n) {
    size_t i;
    for (i = 0; i < n; i++)
        if ((s[i] = t[i]) == '\0') 
            break;
    return s;
}
char* strcat(char* s, const char* t) {
    size_t i, j;
    for (i = strlen(s), j = 0; t[j] != '\0'; i++, j++)
        s[i] = t[j];
}
char* strrev(char* s) {
    size_t front = 0, back = strlen(s) - 1;
    while (front < back) {
        char temp = s[front];
        s[front] = s[back];
        s[back] = temp;
        front++;
        back--;
    }
    return s;
}
size_t strcmp(const char* s, const char* t) {
    size_t i;
    for (i = 0; s[i] == t[i]; i++)
        if (s[i] == '\0')
            return 0;
    return s[i] - t[i];
}
size_t strncmp(const char* s, const char* t, size_t n) {
    size_t i;
    for (i = 0; i < n && s[i] == t[i]; i++)
        if (s[i] == '\0')
            return 0;
    return s[i] - t[i];
}
char* strchr(const char* s, char c) {
    size_t i;
    for (i = 0; s[i] != '\0'; i++)
        if (s[i] == c)
            return s+i;
    return (char*)0;
}
char* strrchr(const char* s, char c);
void* memset(void* s, char v, size_t n) {
    size_t i;
    for (i = 0; i < n; i++) 
        *(char*)(s+i) = v;
    return s;
}
void memcpy(void* s, const void* t, size_t n) {
    size_t i;
    for (i = 0; i < n; i++) {
        *(char*)(s+i) = *(char*)(t+i);
    }
}
size_t memcmp(const void* s, const void* t, size_t n) {
    size_t i;
    for (i = 0; i < n; i++)
        if (*(char*)(s+i) != *(char*)(t+i))
            return *(char*)(s+i) - *(char*)(t+i);
    return 0;
}
