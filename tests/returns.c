
struct div_t {
    int quot;
    int rem;
};

struct div_t div(int num, int den) {
    struct div_t ans;
    ans.quot = 3;
    ans.rem = 4;
    return ans;
}

void print_int(int num) {
    struct div_t ans;
    ans = div(num, 10);
}