struct DivMod {
    int div;
    int mod;
}

char* OUT = 0x7fff;
void put(char c) {
    *OUT = c;
}

struct DivMod* divmod(int n, int d) {
    struct DivMod* ans = 0x7777;
    int q = 0;
    while (n >= d) {
        n -= d;
        q++;
    }
    ans->div = q;
    ans->mod = n;
    return ans;
}

void printnum(int num) {
    struct DivMod* ans;
    do {
        ans = divmod(num, 10);
        put('0' + ans->mod);
    } while (ans->div > 0);
}

void main() {
    struct DivMod* loc = 0x7eee;
}