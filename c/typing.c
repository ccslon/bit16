struct C {
    int d;
    int e[5];
}

void ints() {
    int a;
    a = 0;
    int* aa = &a;
    int copy = a;
}

void arrays() {
    int b[5];
    b[3] = 1;
    int* bb = &b[3];
}

void structs() {
    struct C c;
    c.d = 2;
    int* cc = &c.d;
    struct C ccopy = c;
}



/*
                ; int a;

mov A, 0
ld [sp, 0], A   ; a = 0;


add A, sp, 0
ld [sp, 1], A   ; int* aa = &a;

ld A, [sp, 0]
ld [sp, 2], A   ; int copy = a;

                ; int b[5];

mov A, 1
add B, sp, 0
mov C, 3
ld [B, C], A    ; b[3] = 1;

add A, sp, 0
mov B, 3
add A, B
ld [sp, 1], A   ; int* bb = &b[3];

                ; struct C c;

mov A, 2
add B, sp, 0
mov C, 0
ld [B, C], A    ; c.d = 2;




b[3] = 1;
int* bb = &b[3];

struct C c;
c.d = 2;
struct C* cc = &c.d;
struct C ccopy = c;


*/