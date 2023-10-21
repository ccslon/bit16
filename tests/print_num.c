struct DivMod {
    int div;
    int mod;
};

char* OUT = 0x7fff;
void put(char c) {
    *OUT = c;
}

void print(char* str) {
    while (*str != '\0') {
        put(*str);
        str++;
    }
}

struct DivMod* divmod(int n, int d) {
    struct DivMod* ans;
    ans = 0x7777;
    int q = 0;
    while (n >= d) {
        n -= d;
        q++;
    }
    ans->div = q;
    ans->mod = n;
    return ans;
}

int strlen(char* str) {
    int len = 0;
    while (*str != '\0') {
        str++;
        len++;
    }
    return len;
}

void strrev(char* str) {
    int front = 0;
    int back = strlen(str) - 1;
    while (front < back) {
        int temp = str[front];
        str[front] = str[back];
        str[back] = temp;
        front++;
        back--;
    }
}

void print_num(int num) {
    struct DivMod* ans;
    char buffer[10];
    int i;
    for (i = 0; i < 10; i++) {
        buffer[i] = '\0';
    }
    i = 0;
    do {
        ans = divmod(num, 10);
        buffer[i] = '0' + ans->mod;
        i++;
        num = ans->div;
    } while (num > 0);
    strrev(buffer);
    print(buffer);
}

void main() {
    print_num(123);
}