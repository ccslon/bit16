int isalnum(char c) {
    return isalpha(c) || isdigit(c);
}
int isalpha(char c) {
    return 'A' <= c && c <= 'Z' || 'a' <= c && c <= 'z';
}
int iscntrl(char c) {
    return 0 <= c && c < 32;
}
int isdigit(char c) {
    return '0' <= c && c <= '9';
}
int islower(char c) {
    return 'a' <= c && c <= 'z';
}
int isspace(char c) {
    return c == ' ' || c == '\t' || c == '\n';
}
int isupper(char c) {
    return 'A' <= c && c <= 'Z';
}
int isxdigit(char c) {
    return isdigit(c) || 'A' <= c && c <= 'F' || 'a' <= c && c <= 'f';
}
char tolower(char c) {
    if (isupper(c)) return c + 32;
    return c;
}
char toupper(char c) {
    if (islower(c)) return c - 32;
    return c;
}
int isgraph(char c) {

}
int isprint(char c) {
    
}
int ispunct(char c) {

}