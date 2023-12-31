int strlen(char* str) {
    int len = 0;
    while (*str != '\0') {
        str++;
        len++;
    }
    return len;
}
char* strcpy(char* s, char* t) {
    int i;
    for (i = 0; (s[i] = t[i]) != '\0'; i++) 
        ;
    return s;
}
char* strcat(const char* s, const char* t) {
    int i; int j;
    i = j = 0;
    while (s[i] != '\0') 
        i++;
    while((s[i++] = t[j++]) != '\0')
        ;
}
char* strrev(char* str) {
    int front = 0;
    int back = strlen(str) - 1;
    while (front < back) {
        int temp = str[front];
        str[front] = str[back];
        str[back] = temp;
        front++;
        back--;
    }
    return str;
}
int strcmp(char* s, char* t) {
    int i;
    for (i = 0; s[i] == t[i]; i++)
        if (s[i] == '\0')
            return 0;
    return s[i] - s[i];
}
int strncmp(char* str1, char* str2, int n) {
    int len1 = strlen(str1);
    int len2 = strlen(str2);
    if (len1 != len2) return len1 - len2;
    int i;
    for (i = 0; i < len1 && i < n; i++) {
        if (str1[i] != str2[i]) return str1[i] - str2[i];
    }
    return 0;
}