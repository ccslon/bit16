int isupper(char c) {
    return 'A' <= c && c <= 'Z';
}
int islower(char c) {
    return 'a' <= c && c <= 'z';
}
int isalpha(char c) {
    return islower(c) || isupper(c);
}
int iscntrl(char c) {
    return 0 <= c && c < 32;
}
int isdigit(char c) {
    return '0' <= c && c <= '9';
}
int isalnum(char c) {
    return isalpha(c) || isdigit(c);
}
int isspace(char c) {
    return c == ' ' || c == '\t' || c == '\n';
}
int isxdigit(char c) {
    return isdigit(c) || 'A' <= c && c <= 'F' || 'a' <= c && c <= 'f';
}
char tolower(char c) {
    if (isupper(c))
        return c + 'a' - 'A';
    return c; 
}
char toupper(char c) {
    if (islower(c))
        return c - 'a' - 'A';
    return c;
}
int isgraph(char c) {
    return ' ' < c && c < 0x7f;
}
int isprint(char c) {
    return ' ' <= c && c < 0x7f;
}
int ispunct(char c) {
    return isgraph(c) && !isalnum(c);
}