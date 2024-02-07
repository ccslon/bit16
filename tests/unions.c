void printf(char*, ...);
enum Type {
    STR,
    NUM
};
struct Token {
    enum Type type;
    union Data {
        char* str;
        int num;
    } data;
};
struct Token intToken(int num) {
    struct Token token;
    token.type = NUM;
    token.data.num = num;
    return token;
}
struct Token strToken(char* str) {
    struct Token token;
    token.type = STR;
    token.data.str = str;
    return token;
}
void printToken(struct Token* token) {
    switch (token->type) {
        case STR: {
            printf("(STR, %s)", token->data.str);
            break;
        }
        case NUM: {
            printf("(NUM, %d)", token->data.num);
            break;
        }
    }
}
void main() {
    struct Token t1 = intToken(5);
    printToken(&t1);
    struct Token t2 = strToken("Hello!");
    printToken(&t2);
}