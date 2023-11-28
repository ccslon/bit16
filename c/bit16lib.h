#define div_t struct _div_t_
#define FILE struct _FILE_
#define BUFSIZE 6
div_t {
    int quot;
    int rem;
};
FILE {
    int* buffer;
    int read;
    int write;
};
FILE out = {0x7f00, 0, 0};
int strlen(const char* str) {
    int len = 0;
    while (*str != '\0') {
        str++;
        len++;
    }
    return len;
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
int strcmp(const char* str1, const char* str2) {
    int len1 = strlen(str1);
    int len2 = strlen(str2);
    if (len1 != len2) return len1 - len2;
    int i;
    for (i = 0; i < len1; i++) {
        if (str1[i] != str2[i]) return str1[i] - str2[i];
    }
    return 0;
}
div_t div(int num, int den) {
    div_t ans;
    int quot = 0;
    while (num >= den) {
        num -= den;
        quot++;
    }
    ans.quot = quot;
    ans.rem = num;
    return ans;
}
void put(const char c) {
    out.buffer[out.write++] = c;
}
void print(const char* str) {
    while (*str != '\0') {
        put(*str);
        str++;
    }
}
void println(const char* str) {
    print(str);
    put('\n');
}
void printint(int num) {
    div_t ans;
    char buffer[BUFSIZE];
    int i;
    for (i = 0; i < BUFSIZE; i++) {
        buffer[i] = '\0';
    }
    i = 0;
    do {
        ans = div(num, 10);
        buffer[i] = '0' + ans.rem;
        i++;
        num = ans.quot;
    } while (num > 0);
    strrev(buffer);
    print(buffer);
}