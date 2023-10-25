struct Owner {
    char* name;
    char* email;
};

struct Cat {
    char* name;
    int age;
    struct Owner owner;
};

void stack_cat() {
    struct Cat cat;
    cat.age = 10;
    cat.name = "Cloud";
    cat.owner.name = "Colin";
    cat.owner.email = "ccslon@gmail.com";
}

void init_cat() {
    struct Owner owner = {"Colin", "ccs@email.com"};
    //struct Cat cat = {"Cloud",10,{"Colin", "ccs@email.com"}};
}

/**
.S0: "Cloud\0"
.S1: "Colin\0"
.S2: "ccslon@gmail.com\0"
stack_cat:
  PUSH A, B
  SUB SP, 4
  MOV A, 10
  ADD B, SP, 0
  LD [B, 1], A ; age
  LD A, =.S0
  ADD B, SP, 0
  LD [B, 0], A ; name
  LD A, =.S1
  ADD B, SP, 0
  ADD B, 2
  LD [B, 0], A ; name
  LD A, =.S2
  ADD B, SP, 0
  ADD B, 2
  LD [B, 1], A ; email
  ADD SP, 4
  POP A, B
  RET
.S3: "ccs@email.com\0"
init_cat:
  PUSH A, B
  SUB SP, 6
  ADD A, SP, 0
  LD B, =.S1
  LD [A, 0], B ; name
  LD B, =.S3
  LD [A, 1], B ; email
  ADD A, SP, 2
  LD B, =.S0
  LD [A, 0], B ; name
  MOV B, 10
  LD [A, 1], B ; age
  ADD B, A, 2
  LD C, =.S1
  LD [B, 0], C ; name
  LD C, =.S3
  LD [B, 1], C ; email
  ADD SP, 6
  POP A, B
  RET
*/