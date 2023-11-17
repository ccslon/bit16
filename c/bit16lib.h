#define div_t struct _div_t_
#define FILE struct _FILE_

div_t {
    int div;
    int mod;
};

struct _FILE_ {
    int* buffer;
    int read;
    int write;
};

FILE out = {0x7f00, 0, 0};

int strlen(char* str) {
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
int strcmp(char* str1, char* str2) {
    int len1 = strlen(str1);
    int len2 = strlen(str2);
    if (len1 != len2) return len1 - len2;
    int i;
    for (i = 0; i < len1; i++) {
        if (str1[i] != str2[i]) return str1[i] - str2[i];
    }
    return 0;
}

div_t div(int n, int d) {
    div_t ans;
    int q = 0;
    while (n >= d) {
        n -= d;
        q++;
    }
    ans.div = q;
    ans.mod = n;
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
    char buffer[5];
    int i;
    for (i = 0; i < 5; i++) {
        buffer[i] = '\0';
    }
    i = 0;
    do {
        ans = div(num, 10);
        buffer[i] = '0' + ans.mod;
        i++;
        num = ans.div;
    } while (num > 0);
    strrev(buffer);
    print(buffer);
}