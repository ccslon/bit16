struct DivMod {
    int div;
    int mod;
};

char* OUT = 0x7fff;
void put(char c) {
    *OUT = c;
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

void print_num(int num) {
    struct DivMod* ans;
    do {
        ans = divmod(num, 10);
        put('0' + ans->mod);
        num = ans->div;
    } while (ans->div > 0);
}

void main() {
    print_num(123);
}