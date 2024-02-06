typedef char* str;

typedef struct token {
    str type;
    str lexeme;
    int line;
} Token;

void foo(str s) {
    str lines[3];
    typedef int* word;
    Token token;
    token.type = "NUM";
    token.lexeme = "69";
    word ptr = &token.line;
}