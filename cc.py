# -*- coding: utf-8 -*-
"""
Created on Wed Nov  8 10:16:36 2023

@author: ccslon
"""

'''
TODO

'''

import re
from collections import UserList, UserDict
from bit16 import Reg, Op, Cond

class Loop(UserList):
    def start(self):
        return self[-1][0]
    def end(self):
        return self[-1][1]

class Regs:
    def clear(self):
        self.max = 0
    def __getitem__(self, item):
        if item == 'SP':
            return Reg.SP
        if item > 5:
            raise SyntaxError('Not enough registers =(')
        self.max = max(self.max, item)
        return Reg(item)

r = Regs()

class Frame(UserDict):
    def __init__(self):          
        self.size = 0
        super().__init__()
    def __setitem__(self, name, local):
        local.location = self.size
        self.size += local.type.size
        super().__setitem__(name, local)

class Scope(Frame):
    def __init__(self, old=None):
        if old is None:            
            super().__init__()
        else:            
            self.size = old.size
            self.data = old.data.copy()
class Env:
    def clear(self):
        self.labels = 0
        self.loop = Loop()
        self.globals = {}
        self.strings = []
        self.functions = {}
        self.if_jump_end = False
        self.scope = Scope()
        self.stack = []
        self.structs = {}
    def begin_func(self):
        self.func = None
        self.args = 0
        self.regs = 0
        self.space = 0
        self.returns = False
        self.calls = False
    def begin_scope(self):
        new = Scope(self.scope)
        self.stack.append(self.scope)
        self.scope = new
    def end_scope(self):
        self.scope = self.stack.pop() 
    def begin_loop(self):
        self.loop.append((self.next_label(), self.next_label()))
    def end_loop(self):
        self.loop.pop()
    def next_label(self):
        label = self.labels
        self.labels += 1
        return label

env = Env()

class Emitter:
    def clear(self):
        self.labels = []
        self.asm = []
        self.func = []
    def begin_func(self):
        self.func = []
    def end_func(self):
        self.asm.extend(self.func)
    def add(self, asm):
        for label in self.labels:
            self.func.append(f'{label}:')
        self.func.append(f'  {asm}')
        self.labels.clear()
    def space(self, name, size):
        self.func.append(f'{name}: space {size}')
    def glob(self, name, value):
        self.func.append(f'{name}: {value}')
    def push(self, lr, *regs):
        if lr:
            regs = (Reg.LR,) + regs
        if regs:
            self.func.insert(0, '  PUSH '+', '.join(reg.name for reg in regs))
            # self.add('PUSH '+', '.join(reg.name for reg in regs))
    def pop(self, pc, *regs):
        if pc:
            regs = (Reg.PC,) + regs
        if regs:
            self.add('POP '+', '.join(reg.name for reg in regs))
    def call(self, label):
        self.add(f'CALL {label}')
    def ret(self):
        self.add('RET')
    def load_glob(self, rd, name):
        self.add(f'LD {rd.name}, ={name}')
    def data(self, value):
        self.add(str(value))
    def load(self, rd, rb, offset5=None, name=None):
        self.add(f'LD {rd.name}, [{rb.name}'+(f', {offset5}' if offset5 is not None else '')+']'+(f' ; {name}' if name else ''))
    def store(self, rd, rb, offset5=None, name=None):
        self.add(f'LD [{rb.name}'+(f', {offset5}' if offset5 is not None else '')+f'], {rd.name}'+(f' ; {name}' if name else ''))
    def imm(self, rd, value):
        self.add(f'LD {rd.name}, {value}')
    def loadm(self, rd, size):
        self.add('LDM {'+', '.join(r[rd+i].name for i in range(size))+'}, '+f'{r[size].name}')
    def storem(self, rd, size):
        self.add(f'LDM {r[size].name}'+', {'+', '.join(r[rd+i].name for i in range(size))+'}')
    def inst(self, op, rd, src):
        if op in [Op.NOT, Op.NEG]:
            self.add(f'{op.name} {rd.name}')
        else:
            if type(src) is Reg:
                self.add(f'{op.name} {rd.name}, {src.name}')
            else:
                self.add(f'{op.name} {rd.name}, {src}')    
    def inst3(self, op, rd, rs, rs2):
        self.add(f'{op.name} {rd.name}, {rs.name}, {rs2.name}')
    def inst4(self, op, rd, rs, const4):
        self.add(f'{op.name} {rd.name}, {rs.name}, {const4}')
    def jump(self, cond, target):
        self.add(f'{cond.name} {target}')
    def halt(self):
        self.add('HALT')

emit = Emitter()

class Expr:
    def ret(self, n):
        self.reduce(n)
    def generate(self, n):
        pass
    
class Num(Expr):
    def __init__(self, token):
        value = token.lexeme
        self.token = token
        if value == 'NULL':
            self.value = 0
        elif value.startswith('0x'):
            self.value = int(value, base=16)
        elif value.startswith('0b'):
            self.value = int(value, base=2)
        else:
            self.value = int(value)
    def reduce(self, n):
        if -32 <= self.value < 64:
            emit.inst(Op.MOV, r[n], self.value)
        else:
            emit.imm(r[n], self.value)
        return r[n]

class Char(Expr):
    def __init__(self, token):
        self.token = token
    def reduce(self, n):
        emit.imm(r[n], self.token.lexeme)
        return r[n]

class Unary(Expr):
    OP = {'-':Op.NEG,
          '~':Op.NOT}
    def __init__(self, sign, primary):
        self.sign, self.primary = self.OP[sign.lexeme], primary
    def reduce(self, n):
        emit.inst(self.sign, self.primary.reduce(n), Reg.A)
        return r[n]

class Type(Expr): #TODO
    def __init__(self, type):
        self.type = type
        self.size = 0 if type == 'void' else 1
    def store(self, local, n, base):
        emit.store(r[n], r[base], local.location)
    def address(self, local, n, base):
        emit.inst4(Op.ADD, r[n], r[base], local.location)
        return r[n]
    def reduce(self, local, n, base):
        emit.load(r[n], r[base], local.location)
        return r[n]
    def ret(self, local, n, base):
        self.reduce(local, n, base)

class Const(Type):
    def __init__(self, type):
        self.type = type
        self.size = type.size
        
class Pointer(Type):
    def __init__(self, type):
        self.to = self.of = self.type = type
        self.size = 1

class Struct(Type, Frame):
    def __init__(self, name):
        self.name = name
        self.size = 0
        self.data = {}
    def address(self, local, n, base):
        emit.inst4(Op.ADD, r[n], r[base], local.location) 
        return r[n]
    def store(self, local, n, base):
        self.address(local, n+self.size, base)
        emit.storem(r[n], self.size)
    def reduce(self, local, n, base):
        self.address(local, n+self.size, base)
        emit.loadm(r[n], self.size)
        return r[n]
    def ret(self, local, n, base):
        self.reduce(local, 0, base)
    
class Array(Type):
    def __init__(self, of, length):
        self.size = of.size * length.value
        self.of = of
        self.length = length.value        

class Binary(Expr):    
    OP = {'+' :Op.ADD,
          '++':Op.ADD,
          '+=':Op.ADD,
          '-' :Op.SUB,
          '--':Op.SUB,
          '-=':Op.SUB,
          '*' :Op.MUL,
          '*=':Op.MUL,
          '<<':Op.SHL,
          '<<=':Op.SHL,
          '>>':Op.SHR,
          '>>=':Op.SHR,
          '^' :Op.XOR,
          '^=':Op.XOR,
          '|' :Op.OR,
          '|=':Op.OR,
          '&' :Op.AND,
          '&=':Op.AND,}
    def __init__(self, op, left, right):
        self.op, self.left, self.right = self.OP[op.lexeme], left, right
    def analyze(self, n):
        self.left.analyze(n)
        self.right.analyze_right(n+1)
    def reduce(self, n):        
        emit.inst(self.op, self.left.reduce(n), self.right.reduce(n+1))
        return r[n]

class Assign(Expr):
    def __init__(self, left, right):
        self.left, self.right = left, right
    def analyze(self, n):
        self.right.analyze(n)
        self.left.analyze_store(n)        
    def reduce(self, n):
        self.generate(n)
        return r[n]
    def generate(self, n):
        self.right.reduce(n)
        self.left.store(n)
    
class Block(Expr, UserList):
    def generate(self, n):
        for statement in self:
            statement.generate(n)

class Local(Expr):
    def __init__(self, type, token):
        self.type, self.token = type, token
    def store(self, n):
        return self.type.store(self, n, 'SP') #SP
    def reduce(self, n):
        return self.type.reduce(self, n, 'SP')
    def address(self, n):
        return self.type.address(self, n, 'SP')
    def ret(self, n):
        self.type.ret(self, n, 'SP')

class Attr(Local):
    def store(self, n):
        return self.type.store(self, n, n+1)
    def reduce(self, n):
        return self.type.reduce(self, n, n)
    def address(self, n):
        return self.type.address(self, n, n)
    def ret(self, n):
        self.type.ret(self, n, n)

class Params(Expr, UserList):
    def generate(self):
        for i, param in enumerate(self):
            emit.store(r[i], Reg.SP, i) #env.scope.index(param.id.name))
    
class Func(Expr):
    def __init__(self, type, id, params, block, max_args, space):
        self.type, self.id, self.params, self.block, self.max_args, self.space = type, id, params, block, max_args, space
    def generate(self):
        env.begin_func()
        emit.begin_func()
        r.clear()
        
        if self.space:
            emit.inst(Op.SUB, Reg.SP, self.space)
        if self.type.size: 
            env.return_label = env.next_label()
        self.params.generate()
        self.block.generate(0 if self.max_args is None else self.max_args)
        # print(env.args, env.regs)
        emit.func.append(f'.L{env.return_label}:')
        if type(self.type) is not Struct and self.max_args is not None and self.max_args > 0:
            emit.inst(Op.MOV, Reg.A, r[self.max_args])
        if self.space:
            emit.inst(Op.ADD, Reg.SP, self.space)
        print(r.max)
        push = list(map(Reg, range(max(len(self.params), self.type.size), r.max+1))) #(0 if self.max_args is None else self.max_args) + 
        emit.push(self.max_args is not None, *push)
        emit.pop(self.max_args is not None, *push)
        emit.func.insert(0, f'{self.id.lexeme}:')
        if self.max_args is None:
            emit.ret()
        emit.end_func()

class Main(Expr):
    def __init__(self, block):
        self.block = block
    def generate(self):
        env.begin_func()
        # self.block.analyze(1)
        # if env.space:
        #     emit.inst(Op.SUB, Reg.SP, env.space)
        self.block.compile(0)
        # if env.space:
        #     emit.inst(Op.ADD, Reg.SP, env.space)
        emit.halt()

class Dot(Expr):
    def __init__(self, postfix, attr):
        self.postfix, self.attr = postfix, attr
        self.type = attr.type
    def address(self, n):
        emit.inst(Op.ADD, self.postfix.address(n), self.attr.location)
        return r[n]
    def store(self, n):
        self.postfix.address(n+1)
        return self.attr.store(n)
    def reduce(self, n):
        self.postfix.address(n)
        return self.attr.reduce(n)

class Arrow(Expr):
    def __init__(self, postfix, attr):
        self.postfix, self.attr = postfix, attr
        self.type = attr.type
    def address(self, n):
        emit.inst(Op.ADD, self.postfix.address(n), self.attr.location)
        return r[n] 
    def store(self, n):
        self.postfix.address(n+1)
        return self.attr.store(n)
    def reduce(self, n):
        self.postfix.address(n)
        return self.attr.reduce(n)

class SubScr(Expr): 
    def __init__(self, postfix, sub):
        self.postfix, self.sub = postfix, sub
        self.type = self.postfix.type.of
    def address(self, n):
        self.postfix.reduce(n)
        self.sub.reduce(n+1)
        if type(self.postfix.type) in [Array, Pointer] and self.postfix.type.of.size > 1:
            emit.inst(Op.MUL, r[n+1], self.postfix.type.of.size)
        emit.inst(Op.ADD, r[n], r[n+1])
        return r[n]
    def store(self, n):
        emit.store((n), self.address(n+1))
        return r[n]
    def reduce(self, n):
        emit.load(self.address(n), r[n])
        return r[n]

class Args(Expr, UserList):
    def generate(self, n):
        for i, arg in enumerate(self, n):
            arg.reduce(i)
        if n > 0:
            for i, arg in enumerate(self):
                emit.inst(Op.MOV, r[i], r[n+i]) 

class Call(Expr): #TODO
    def __init__(self, postfix, args):
        self.primary, self.args = postfix, args
    def reduce(self, n):
        return self.generate(n)
    def generate(self, n):
        self.args.generate(n)
        emit.call(self.primary.token.lexeme)
        if n > 0:
            emit.inst(Op.MOV, r[n], Reg.A)
        return r[n]

class Return(Expr):
    def __init__(self):
        self.expr = None
        # self.type = Type('void')
    def generate(self, n):
        # assert self.type() == env.func.type_spec, f'{self.expr.type()} != {env.func.type_spec} in {env.func.id.name}'       
        if self.expr:
            self.expr.ret(n)
        emit.jump(Cond.JR, f'.L{env.return_label}')

class Program(Expr, UserList):
    def generate(self):
        for statement in self:
            statement.generate()
        return '\n'.join(emit.asm)

class Token:
    def __init__(self, type, lexeme, line_no):
        self.type, self.lexeme, self.line_no = type, lexeme, line_no

class MetaLexer(type):
    def __init__(self, name, bases, attrs):
        self.action = {}
        regex = []        
        flag = attrs['flag'] if 'flag' in attrs else 0 #re.NOFLAG
        for attr in attrs:
            if attr.startswith('RE_'):
                name = attr[3:]
                if callable(attrs[attr]):
                    pattern = attrs[attr].__doc__
                    self.action[name] = attrs[attr]
                else:
                    pattern = attrs[attr]
                    self.action[name] = lambda self, match: match
                regex.append((name, pattern))
        self.regex = re.compile('|'.join(rf'(?P<{name}>{pattern})' for name, pattern in regex), flag)

class LexerBase(metaclass=MetaLexer):
    def lex(self, text):
        return [Token(match.lastgroup, result, self.line_no) for match in self.regex.finditer(text) if (result := self.action[match.lastgroup](self, match.group())) is not None] + [Token('end','',self.line_no)]

class CLexer(LexerBase):    
    def __init__(self):
        self.line_no = 1
    
    RE_num = r'(0x[0-9a-f]+)|(0b[01]+)|(\d+)|(NULL)'
    RE_char = r"'\\?[^']'"
    RE_const = r'const'
    RE_type = r'\b((void)|(int)|(char))\b'
    RE_struct = r'\bstruct\b'
    RE_return = r'\breturn\b'
    RE_id = r'\w(\w|\d)*'
    def RE_comment(self, match):
        r'/\*(?:(?!/\*).|\n)*\*/'
        self.line_no += match.count('\n')
    def RE_line_comment(self, match):
        r'//[^\n]*\n'
        self.line_no += 1
    def RE_new_line(self, match):
        r'\n'
        self.line_no += 1
    RE_semi = r';'
    RE_lparen = r'\('
    RE_rparen = r'\)'
    RE_lbrack = r'{'
    RE_rbrack = r'}'
    RE_lbrace = r'\['
    RE_rbrace = r'\]'
    RE_dplus = r'\+\+'
    RE_ddash = r'--'
    RE_arrow = r'->'
    RE_pluseq = r'\+='
    RE_dasheq = r'-='
    RE_stareq = r'\*='
    RE_slasheq = r'/='
    RE_percenteq = r'%='
    RE_lshifteq = r'<<='
    RE_rshifteq = r'>>='
    RE_careteq = r'\^='
    RE_pipeeq = r'\|='
    RE_ampeq = r'&='
    RE_eq = r'='
    RE_plus =  r'\+'
    RE_dash = r'-'
    RE_star = r'\*'
    RE_slash = r'/'
    RE_percent = r'%'
    RE_lshift = r'<<'
    RE_rshift = r'>>'
    RE_caret = r'\^'
    RE_pip = r'\|'
    RE_amp = r'\&'   
    RE_exp = r'!'
    RE_tilde = r'~'
    RE_dot = r'\.'
    RE_comma = r','
    def RE_error(self, match):
        r'\S'
        raise SyntaxError(f'line {self.line_no}: Invalid symbol "{match}"')

lexer = CLexer()

class CParser:
    def resolve(self, name):
        if name in env.scope:
            return env.scope[name]
        elif name in env.functions:
            return env.functions[name]
        else:
            self.error(f'name "{name}" not found')
    def primary(self):
        '''
        PRIMARY -> id|num|char|string|'(' EXPR ')'
        '''
        if self.peek('id'):
            return self.resolve(next(self).lexeme)
        elif self.peek('num'):
            return Num(next(self))
        elif self.peek('char'):
            return Char(next(self))
        elif self.accept('('):
            primary = self.expr()
            self.expect(')')
        else:
            self.error('PRIMARY EXPRESSION')
        return primary
    
    def postfix(self):
        '''
        POST -> PRIMARY {'[' EXPR ']'|'(' ARGS ')'|'.' id|'->' id|'++'|'--'}
        '''
        postfix = self.primary()
        while self.peek('.','[','->','('):
            if self.accept('.'):
                postfix = Dot(postfix, postfix.type[self.expect('id').lexeme])
            elif self.accept('['):
                postfix = SubScr(postfix, self.expr())
                self.expect(']')
            elif self.accept('->'):
                postfix = Arrow(postfix, postfix.type.to[self.expect('id').lexeme])
            elif self.accept('('):
                # TODO assert type(postfix) is ...
                postfix = Call(postfix, self.args())
                self.expect(')')
                if env.calls is None:
                    env.calls = 0
                env.calls = max(env.calls, len(postfix.args))
            else:
                self.error('POSTFIX EXPRESSION')
        return postfix
    
    def args(self):
        '''
        ARGS -> ASSIGN {',' ASSIGN}
        '''
        args = Args()
        if not self.peek(')'):
            args.append(self.assign())
            while self.accept(','):
                args.append(self.assign())
        return args
    
    def unary(self):
        '''
        UNARY -> POSTFIX
                |('++'|'--') UNARY
                |('-'|'~'|'!'|'*'|'&') CAST
                |'sizeof' UNARY
                |'sizeof' '(' TYPE_SPEC ')'
        '''
        if self.peek('-','~',):
            return Unary(next(self), self.unary())
        else:
            return self.postfix()
    
    def type_spec(self):
        '''
        TYPE_SPEC -> (type|(('struct'|'union') id)) {'*'}
        '''
        if self.peek('type'):
            type_spec = Type(next(self))
        elif self.accept('struct'):
            type_spec = env.structs[self.expect('id').lexeme]
        else:
            self.error('TYPE SPECIFIER')
        return type_spec
    
    def type_qual(self):
        '''
        TYPE_QUAL -> 'const' TYPE_SPEC
        '''
        if self.accept('const'):
            return Const(self.type_spec())
        return self.type_spec()
    
    def mul(self):
        '''
        MUL -> UNARY {('*'|'/'|'%') UNARY}
        '''
        mul = self.unary()
        while self.peek('*'):
            mul = Binary(next(self), mul, self.unary())
        return mul
    
    def add(self):
        '''
        ADD -> MUL {('+'|'-') MUL}
        '''
        add = self.mul()
        while self.peek('+','-'):
            add = Binary(next(self), add, self.mul())
        return add
            
    def shift(self):
        '''
        SHIFT -> ADD {('<<'|'>>') ADD}
        '''
        shift = self.add()
        while self.peek('<<','>>'):
            shift = Binary(next(self), shift, self.add())
            self.add()
        return shift
    
    def assign(self):
        '''
        ASSIGN -> UNARY ['+'|'-'|'*'|'/'|'%'|'<<'|'>>'|'^'|'|'|'&']'=' ASSIGN
                 |COND
        '''
        assign = self.shift()
        if self.accept('='):
            assert isinstance(assign, (Local,Dot,Arrow))
            assign = Assign(assign, self.assign())
        elif self.peek('+=','-=','*=','/=','%=','<<=','>>=','^=','|=','&='):
            assert isinstance(assign, (Local,Dot,Arrow))
            assign = Assign(assign, Binary(next(self), assign, self.assign()))
        return assign
    
    def expr(self):
        '''
        EXPR -> ASSIGN
        '''
        return self.assign()
        # while self.accept(','):
        #     self.assign()
    
    def const_expr(self):
        '''
        CONST -> EXPR
        '''
        return self.expr()
             
    def statement(self):
        '''
        STATE -> '{' BLOCK '}'
                |SELECT
                |LOOP
                |JUMP
                |ASSIGN ';'
        SELECT -> 'if' '(' EXPR ')' STATE ['else' STATE]|'switch' '(' EXPR ')' '{' {'case' CONST_EXPR ':' STATEMENT} ['default' ':' STATEMENT] '}'
        LOOP -> 'while' '(' EXPR ')' STATE|'for' '(' EXPR ';' EXPR ';' EXPR ')' STATE|'do' STATEMENT 'while' '(' EXPR ')' ';'
        JUMP -> 'goto' ';'|'return' [EXPR] ';' |'break' ';' |'continue' ';'
        '''
        if self.accept('{'):            
            env.begin_scope()
            statement = self.block()
            env.end_scope()
            self.expect('}')
        elif self.accept('return'):
            statement = Return()
            if not self.accept(';'):
                statement.expr = self.expr()
                self.expect(';')
        else:
            statement = self.assign()
            assert isinstance(statement, (Assign, Call))
            self.expect(';')
        return statement    

    def block(self):
        '''
        BLOCK -> {DECL} {STATE} [BLOCK]
        '''
        block = Block()
        while self.peek('const','type','struct','union'):
            block.append(self.init())
        while self.peek('{','id','++','--','return'):
            block.append(self.statement())
        if not (self.peek('}') or self.peek('end')):# or (len(block) > 0):
            block.extend(self.block())        
        return block
    
    def init(self):
        '''
        INIT -> DECL ['=' EXPR] ';'
        '''
        init = self.decl()
        if self.accept('='):
            init = Assign(init, self.expr())
        self.expect(';')
        return init
    
    def abstract(self):
        abstract = self.type_qual()
        while self.accept('*'):
            abstract = Pointer(abstract)
        return abstract
    
    def decl(self):
        '''
        DECL -> TYPE_QUAL id {'[' [num] ']'}
        '''
        type = self.abstract()
        id = self.expect('id')
        #Array here
        local = Local(type, id)
        env.scope[id.lexeme] = local
        env.space += type.size
        return local

    def params(self):
        '''
        PARAMS -> [DECL {',' DECL}]
        '''
        params = Params()
        if self.peek('const','type','struct','union'):    
            params.append(self.decl())
            while self.accept(','):
                params.append(self.decl())
        return params
    
    def program(self):
        program = Program()
        while self.peek('type','const','struct'):
            if self.peekn('struct','id','{'):
                next(self)
                id = next(self)
                next(self)
                struct = Struct(id.lexeme)
                env.structs[id.lexeme] = struct
                while not self.accept('}'):
                    type = self.abstract()
                    id = self.expect('id')
                    struct[id.lexeme] = Attr(type, id)
                    self.expect(';')
                self.expect(';')
            else:
                type = self.abstract()
                id = self.expect('id')
                if self.accept('('):                    #Function
                    env.calls = None
                    env.space = 0
                    env.begin_scope()
                    params = self.params()
                    self.expect(')')
                    self.expect('{')
                    block = self.block()
                    env.end_scope()
                    self.expect('}')
                    #add function to scope/locals
                    # print(env.scope)
                    env.functions[id.lexeme] = Local(type, id)
                    if id.lexeme == 'main':
                        program.insert(0, Main(block))
                    else:
                        program.append(Func(type, id, params, block, env.calls, env.space))
                else:                                   #Global
                    pass
        return program
    
    def parse(self, text):
        self.included = set()
        self.tokens = lexer.lex(text)
        # for i, t in enumerate(self.tokens): print(i, t.type, t.lexeme)
        self.index = 0
        program = self.program()
        self.expect('end')
        return program
        
    def __next__(self):
        token = self.tokens[self.index]
        self.index += 1
        return token
        
    def peek(self, *symbols, offset=0):
        token = self.tokens[self.index+offset]
        return token.type in symbols or (not token.lexeme.isalnum() and token.lexeme in symbols)
    
    def peekn(self, *buckets):
        if self.index+len(buckets) < len(self.tokens)-1:
            for i, bucket in enumerate(buckets):
                if type(bucket) is str:
                    bucket = (bucket,)
                if not self.peek(*bucket, offset=i):
                    return False
            return True
        return False
            
    
    def peek2(self, sym1, sym2):
        if self.index < len(self.tokens) - 1:            
            return self.peek(sym1) and self.peek(sym2, offset=1)
    
    def accept(self, *symbols):
        if self.peek(*symbols):
            return next(self)
    
    def expect(self, symbol):
        if self.peek(symbol):
            return next(self)
        self.error(symbol)
        
    def error(self, expected=None):
        error = self.tokens[self.index]
        raise SyntaxError(f'Line {error.line_no}: Unexpected {error.type} token "{error.lexeme}".'+ (f' Expected "{expected}"' if expected is not None else ''))
        
parser = CParser()

def parse(text):
    return parser.parse(text)

test = '''
struct Owner {
    int name;
    int phone;
};
struct Cat {
    int name;
    int age;
    struct Owner owner;
};

void test() {
    int foo;
    int bar = 9;
    foo = 8;
    int baz = foo + -bar;
    {
     char foo;
     foo = 'g';
    }
    foo = 5;
    const int* ptr = 6;
}

void test2(int foo) {
    struct Owner me;
    me.name = 100;
    me.phone = 1000;
    int bar = me.name;
}

void tset3() {
    struct Cat cat;
    cat.name = 1;
    cat.age = 10;
    cat.owner.name = 100;
    cat.owner.phone = 1000;
}

void test4(struct Cat* cat) {
    cat->name = 1;
    cat->age = 10;
    cat->owner.name = 100;
}
void test5(struct Cat* cats) {
    cats[0].name = 1;
}
int getint() {
    return 1;
}

void test6() {
    int i = getint();
}

void test7() {
    struct Cat cat1;
    struct Cat cat2;
    cat2 = cat1;
}
'''
'''
  MOV A, 9
  LD [SP, 1], A
  MOV A, 8
  LD [SP, 0], A
  LD A, [SP, 0]
  LD B, [SP, 1]
  NEG B
  ADD A, B
  LD [SP, 2], A
  LD A, 'g'
  LD [SP, 3], A
  MOV A, 5
  LD [SP, 0], A
  MOV A, 6
  LD [SP, 3], A
  RET
test2:
  LD [SP, 0], A
  LD A, 100
  ADD B, SP, 1
  LD [B, 0], A
  LD A, 1000
  ADD B, SP, 1
  LD [B, 1], A
  ADD A, SP, 1
  LD A, [A, 0]
  LD [SP, 3], A
  RET
tset3:
  MOV A, 1
  ADD B, SP, 0
  LD [B, 0], A
  MOV A, 10
  ADD B, SP, 0
  LD [B, 1], A
  LD A, 100
  ADD B, SP, 0
  ADD B, 2
  LD [B, 0], A
  LD A, 1000
  ADD B, SP, 0
  ADD B, 2
  LD [B, 1], A
  RET
test4:
  LD [SP, 0], A
  MOV A, 1
  LD B, [SP, 0]
  LD [B, 0], A
  MOV A, 10
  LD B, [SP, 0]
  LD [B, 1], A
  LD A, 100
  ADD B, SP, 0
  ADD B, 2
  LD [B, 0], A
  RET
'''

test2 = '''
struct Owner {
    int name;
    int phone;
};
struct Cat {
    int name;
    int age;
    struct Owner owner;
};

void test() {
    struct Owner me;
    int name = me.name;
}

struct div_t {
    int quot;
    int rem;
};

struct div_t div(int num, int den) {
    struct div_t ans;
    ans.quot = num;
    ans.rem = den;
    return ans;
}

void test2() {
    struct Owner me;
    struct Owner you;
    me = you;
}

int bar(int m, int c) {
    return m + c;
}

int foo(int n) {
    return bar(n, 5);
}
'''

if __name__ == '__main__':
    env.clear()
    emit.clear()
    ast = parse(test2.strip('\n'))
    asm = ast.generate()
    print(asm.strip('\n'))