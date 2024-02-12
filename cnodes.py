# -*- coding: utf-8 -*-
"""
Created on Mon Jul  3 19:48:36 2023

@author: Colin
"""
from collections import UserList, UserDict
from bit16 import Reg, Op, Cond

class Loop(UserList):
    def start(self):
        return self[-1][0]
    def end(self):
        return self[-1][1]
    
class Regs:
    def clear(self):
        self.max = -1
    def __getitem__(self, item):
        if item == 'FP':
            return Reg.FP
        elif item > Reg.D:
            # print('\n'.join(emit.asm))
            raise SyntaxError('Not enough registers =(')
        self.max = max(self.max, item)
        return Reg(item)

regs = Regs()

class Frame(UserDict):
    def __init__(self):
        super().__init__()    
        self.size = 0
    def __setitem__(self, name, local):
        local.location = self.size
        self.size += local.type.size
        super().__setitem__(name, local)
        
class Environment:
    def clear(self):
        self.labels = 0
        self.loop = Loop()
        self.if_jump_end = False
        self.preview = False
    def begin_func(self, defn):
        self.defn = defn
        self.space = defn.space
    def begin_loop(self):
        self.loop.append((self.next_label(), self.next_label()))
    def end_loop(self):
        self.loop.pop()
    def next_label(self):
        if not self.preview:
            label = self.labels
            self.labels += 1
            return label

env = Environment()

class Emitter:
    def clear(self):
        self.labels = []
        self.asm = []
        self.data = []
        self.strings = []
        self.preview = False
    def string(self, string):
        if not self.preview:
            if string not in self.strings:
                self.strings.append(string)
                emit.glob(f'.S{self.strings.index(string)}', string)
            return f'.S{self.strings.index(string)}'
    def append_label(self, label):
        if not self.preview:
            self.labels.append(label)
    def add(self, asm):
        if not self.preview:
            for label in self.labels:
                self.asm.append(f'{label}:')
            self.asm.append(f'  {asm}')
            self.labels.clear()
    def space(self, name, size):
        if not self.preview:
            self.data.append(f'{name}: space {size}')
    def glob(self, name, value):
        if not self.preview:
            self.data.append(f'{name}: {value}')
    def datas(self, label, datas):
        if not self.preview:
            self.data.append(f'{label}:')
            for data in datas:
                self.data.append(f'  {data}')
    def push(self, reg):
        self.add(f'PUSH {reg.name}')
    def pop(self, reg):
        self.add(f'POP {reg.name}')
    def pushm(self, calls, *regs):
        if calls:
            regs = (Reg.LR,) + regs
        self.add('PUSH '+', '.join(reg.name for reg in regs))
    def popm(self, calls, *regs):
        if calls:
            regs = (Reg.LR,) + regs
        self.add('POP '+', '.join(reg.name for reg in regs))
    def call(self, proc):
        if isinstance(proc, str):
            self.add(f'CALL {proc}')
        else:
            self.add(f'CALL {proc.name}')
    def ret(self):
        self.add('RET')
    def load_glob(self, rd, name):
        self.add(f'LD {rd.name}, ={name}')
    def load(self, rd, rb, offset5=None, name=None):
        self.add(f'LD {rd.name}, [{rb.name}'+(f', {offset5}' if offset5 is not None else '')+']'+(f' ; {name}' if name else ''))
    def store(self, rd, rb, offset5=None, name=None):
        self.add(f'LD [{rb.name}'+(f', {offset5}' if offset5 is not None else '')+f'], {rd.name}'+(f' ; {name}' if name else ''))
    def imm(self, rd, value):
        self.add(f'LD {rd.name}, {value}')
    def loadm(self, rd, size):
        self.add('LDM {'+', '.join(regs[rd+i].name for i in range(size))+'}, '+f'{regs[size].name}')
    def storem(self, rd, size):
        self.add(f'LDM {regs[size].name}'+', {'+', '.join(regs[rd+i].name for i in range(size))+'}')
    def inst(self, op, rd, src):
        if op in [Op.NOT, Op.NEG]:
            self.add(f'{op.name} {rd.name}')
        else:
            if type(src) is Reg:
                self.add(f'{op.name} {rd.name}, {src.name}')
            else:
                self.add(f'{op.name} {rd.name}, {src}')
    def inst3c(self, op, rd, rs, const4):
        self.add(f'{op.name} {rd.name}, {rs.name}, {const4}')
    def jump(self, cond, target):
        self.add(f'{cond.name} {target}')
    def halt(self):
        if not self.preview:
            self.add('HALT')

emit = Emitter()

class CNode:
    def generate(self, n):
        pass

class Void(CNode):
    def __init__(self):
        self.size = 0
    def __eq__(self, other):
        return type(other) is Void
    def __str__(self):
        return 'void'

class Type(CNode):
    def __init__(self, type):
        self.type = type
        self.size = 1
    @staticmethod
    def store(local, n, base):
        if local.location is None:
            emit.load_glob(regs[n+1], local.token.lexeme)
            emit.store(regs[n], regs[n+1])
        else:
            emit.store(regs[n], regs[base], local.location, local.token.lexeme)
        return regs[n]
    @staticmethod
    def address(local, n, base):
        if -8 <= local.location < 8:
            emit.inst3c(Op.ADD, regs[n], regs[base], local.location)
        elif -32 <= local.location < 32:
            emit.inst(Op.MOV, regs[n], regs[base])
            emit.inst(Op.ADD, regs[n], local.location)
        return regs[n]
    @staticmethod
    def reduce(local, n, base):
        if local.location is None:
            emit.load_glob(regs[n], local.token.lexeme)
            emit.load(regs[n], regs[n])
        else:
            emit.load(regs[n], regs[base], local.location, local.token.lexeme)
        return regs[n]
    @staticmethod
    def glob(glob):
        if glob.init:
            emit.glob(glob.token.lexeme, glob.init.value)
        else:
            emit.space(glob.token.lexeme, glob.type.size)
    def cast(self, other):
        return type(other) in [Pointer, VoidPtr, Type] \
            or type(other) is Const and self.cast(other.type)
    def __eq__(self, other):
        return type(other) is Type
    def __str__(self):
        return self.type

class VoidPtr(Type):
    def cast(self, other):
        return type(other) in [Pointer, VoidPtr, Type] \
            or type(other) is Const and self.cast(other.type)
    def __eq__(self, other):
        return type(other) in [VoidPtr, Pointer]

class Const(Type):
    def __init__(self, type):
        super().__init__(type)
        self.size = type.size
    def cast(self, other):
        return self == other
    def __eq__(self, other):
        return self.type == other \
            or type(other) is Const and self.type == other.type
    def __str__(self):
        return f'const {self.type}'
    
class Pointer(Type):
    def __init__(self, type):
        super().__init__(type)
        self.to = self.of = self.type
        self.size = 1
    @staticmethod
    def reduce(local, n, base):
        if local.location is None:
            emit.load_glob(regs[n], local.token.lexeme)
        else:
            emit.load(regs[n], regs[base], local.location, local.token.lexeme)
        return regs[n]
    def cast(self, other):
        return type(other) in [Pointer, VoidPtr, Type] \
            or type(other) is Const and self.cast(other.type)
    def __eq__(self, other):
        return type(other) is Pointer and self.to == other.to \
            or type(other) is Array and self.of == other.of \
            or type(other) is VoidPtr
    def __str__(self):
        return f'{self.to}*'

class Struct(Frame, Type):
    def __init__(self, name):
        super().__init__()
        self.name = name
    @staticmethod
    def store(local, n, base):
        Struct.address(local, n+1, base)
        for i in range(local.type.size):
            emit.load(regs[n+2], regs[n], i)
            emit.store(regs[n+2], regs[n+1], i)
    @staticmethod
    def reduce(local, n, base):
        return Struct.address(local, n, base)
    @staticmethod
    def glob(glob):
        if glob.init:
            emit.datas(glob.token.lexeme, [expr.data() for expr in glob.init])
        else:
            emit.space(glob.token.lexeme, glob.type.size)
    def cast(self, other):
        return self == other
    def __eq__(self, other):
        return type(other) is Struct and self.name == other.name
    def __str__(self):
        return f'struct {self.name}'

class Union(UserDict, Type): #TODO
    def __init__(self, name):
        super().__init__()
        self.size = 0
        self.name = name
    def __setitem__(self, name, attr):
        attr.location = 0
        self.size = max(self.size, attr.type.size)
        super().__setitem__(name, attr)

class Array(Type):
    def __init__(self, of, length):
        self.size = of.size * length.value
        self.of = of
        self.length = length.value
    @staticmethod
    def address(local, n, base):
        if local.location is None:
            emit.load_glob(regs[n], local.token.lexeme)
        else:
            Type.address(local, n, base)
        return regs[n]
    @staticmethod
    def reduce(local, n, base):
        return Array.address(local, n, base)
    @staticmethod
    def glob(glob):
        if glob.init:
            emit.datas(glob.token.lexeme, [expr.data() for expr in glob.init])
        else:
            emit.space(glob.token.lexeme, glob.type.size)
    def cast(self, other):
        return self == other
    def __eq__(self, other):
        return type(other) is Array and self.of == other.of
    def __str__(self):
        return f'{self.of}[]'

class Expr(CNode):
    def __init__(self, type, token):
        self.type = type
        self.token = token
    def branch_reduce(self, n , _):
        self.reduce(n)
    def branch(self, n, _):
        self.generate(n)
    def compare(self, n, label):
        emit.inst(Op.CMP, self.reduce(n), 0)
        emit.jump(Cond.JEQ, f'.L{label}')
    def compare_false(self, n, label):
        emit.inst(Op.CMP, self.reduce(n), 0)
        emit.jump(Cond.JNE, f'.L{label}')
    def num_reduce(self, n):
        return self.reduce(n)
    
class NumBase(Expr):
    def __init__(self, token):
        super().__init__(Type('int'), token)
    def data(self):
        return self.value
    def reduce(self, n):
        if -32 <= self.value < 32:
            emit.inst(Op.MOV, regs[n], self.value)
        else:
            emit.imm(regs[n], self.value)
        return regs[n]
    def num_reduce(self, n):
        if -32 <= self.value < 32:
            return self.value
        else:
            emit.imm(regs[n], self.value)
            return regs[n]

class EnumConst(NumBase):
    def __init__(self, token, value):
        super().__init__(token)
        self.value = value

class Num(NumBase):
    def __init__(self, token):
        super().__init__(token)
        if token.lexeme == 'NULL':
            self.value = 0
        elif token.lexeme.startswith('0x'):
            self.value = int(token.lexeme, base=16)
        elif token.lexeme.startswith('0b'):
            self.value = int(token.lexeme, base=2)
        else:
            self.value = int(token.lexeme)    

class SizeOf(NumBase):
    def __init__(self, token, abstract):
        super().__init__(token)
        self.value = abstract.type.size

class Char(Expr):
    def __init__(self, token):
        super().__init__(Type('char'), token)
    def data(self):
        return self.token.lexeme
    def reduce(self, n):
        emit.imm(regs[n], self.data())
        return regs[n]

class String(Expr):
    def __init__(self, token):
        super().__init__(Pointer(Type('char')), token)
        self.value = f'"{token.lexeme[1:-1]}\\0"'
    def data(self):
        return emit.string(self.value)
    def reduce(self, n):
        emit.load_glob(regs[n], self.data())
        return regs[n]

class OpExpr(Expr):
    OP = {}
    def __init__(self, type, op):
        super().__init__(type, op)
        self.op = self.OP[op.lexeme]

class Unary(OpExpr):
    OP = {'-':Op.NEG,
          '~':Op.NOT}
    def __init__(self, op, unary):
        assert unary.type.cast(Type('int')), f'Line {op.line}: Cannot {op.lexeme} {unary.type}'
        super().__init__(unary.type, op)
        self.unary = unary
    def reduce(self, n):
        emit.inst(self.op, self.unary.reduce(n), Reg.A)
        return regs[n]
    
class Pre(Unary):
    OP = {'++':Op.ADD,
          '--':Op.SUB}
    def reduce(self, n):
        self.generate(n)
        return regs[n]
    def generate(self, n):
        self.unary.reduce(n)
        emit.inst(self.op, regs[n], 1)
        self.unary.store(n)

class AddrOf(Expr):
    def __init__(self, token, unary):
        super().__init__(Pointer(unary.type), token)
        self.unary = unary
    def reduce(self, n):
        return self.unary.address(n)

class Deref(Expr):
    def __init__(self, token, unary):
        assert hasattr(unary.type, 'to'), f'Line {token.line}: Cannot {token.lexeme} {unary.type}'
        super().__init__(unary.type.to, token)
        self.unary = unary
    def store(self, n):
        self.unary.reduce(n+1)
        emit.store(regs[n], regs[n+1])
    def reduce(self, n):
        self.unary.reduce(n)
        emit.load(regs[n], regs[n])
        return regs[n]  

class Cast(Expr):
    def __init__(self, type, token, cast):
        assert type.cast(cast.type), f'Line {token.line}: Cannot cast {cast.type} to {type}'
        super().__init__(type, token)
        self.cast = cast
    def reduce(self, n):
        return self.cast.reduce(n)
    def data(self):
        return self.cast.data()
    
class Not(Expr):
    def __init__(self, token, unary):
        super().__init__(unary.type, token)
        self.unary = unary        
    def compare(self, n, label):
        emit.inst(Op.CMP, self.unary.reduce(n), 0)
        emit.jump(Cond.JNE, f'.L{label}')
    def compare_false(self, n, label):
        emit.inst(Op.CMP, self.unary.reduce(n), 0)
        emit.jump(Cond.JEQ, f'.L{label}')
    def reduce(self, n):
        label = env.next_label()
        sublabel = env.next_label()
        self.unary.compare(n, sublabel)
        emit.inst(Op.MOV, Reg(n), 0)
        emit.jump(Cond.JR, f'.L{label}')
        emit.append_label(f'.L{sublabel}')
        emit.inst(Op.MOV, Reg(n), 1)
        emit.append_label(f'.L{label}')
        return regs[n]

class Binary(OpExpr):
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
          '&=':Op.AND,
          '/': '_div',
          '/=':'_div',
          '%': '_mod',
          '%=':'_mod'}
    def __init__(self, op, left, right):
        assert left.type.cast(right.type), f'Line {op.line}: Cannot {left.type} {op.lexeme} {right.type}'
        super().__init__(left.type, op)
        self.left, self.right = left, right
    def reduce(self, n):
        if self.op in ['_div','_mod']:
            self.right.reduce(n)
            emit.push(regs[n])
            self.left.reduce(n)
            emit.push(regs[n])
            emit.call(self.op)
            if n > 0:
                emit.inst(Op.MOV, regs[n], Reg.A)    
        else:
            emit.inst(self.op, self.left.reduce(n), self.right.num_reduce(n+1))
        return regs[n]

class Compare(Binary):
    OP = {'==':Cond.JEQ,
          '!=':Cond.JNE,
          '>': Cond.JGT,
          '<': Cond.JLT,
          '>=':Cond.JGE,
          '<=':Cond.JLE}
    INV = {'==':Cond.JNE,
           '!=':Cond.JEQ,
           '>': Cond.JLE,
           '<': Cond.JGE,
           '>=':Cond.JLT,
           '<=':Cond.JGT}
    def __init__(self, op, left, right):
        super().__init__(op, left, right)
        self.inv = self.INV[op.lexeme]
    def compare(self, n, label):        
        emit.inst(Op.CMP, self.left.reduce(n), self.right.num_reduce(n+1))
        emit.jump(self.inv, f'.L{label}')
    def compare_false(self, n, label):
        emit.inst(Op.CMP, self.left.reduce(n), self.right.num_reduce(n+1))
        emit.jump(self.op, f'.L{label}')
    def reduce(self, n):        
        label = env.next_label()
        sublabel = env.next_label()
        self.compare(n, sublabel)
        emit.inst(Op.MOV, Reg(n), 1)
        emit.jump(Cond.JR, f'.L{label}')
        emit.append_label(f'.L{sublabel}')
        emit.inst(Op.MOV, Reg(n), 0)
        emit.append_label(f'.L{label}')
        return Reg(n)

class Logic(Binary):
    OP = {'&&':Op.AND,
          '||':Op.OR}
    def compare(self, n, label):
        if self.op == Op.AND:
            emit.inst(Op.CMP, self.left.reduce(n), 0)
            emit.jump(Cond.JEQ, f'.L{label}')
            emit.inst(Op.CMP, self.right.reduce(n), 0)
            emit.jump(Cond.JEQ, f'.L{label}')
        elif self.op == Op.OR:
            sublabel = env.next_label()
            emit.inst(Op.CMP, self.left.reduce(n), 0)
            emit.jump(Cond.JNE, f'.L{sublabel}')
            emit.inst(Op.CMP, self.right.reduce(n), 0)
            emit.jump(Cond.JEQ, f'.L{label}')
            emit.append_label(f'.L{sublabel}')

class Condition(Expr):
    def __init__(self, cond, true, false):
        self.type = true.type
        self.cond, self.true, self.false = cond, true, false
    def reduce(self, n):
        env.if_jump_end = False
        label = env.next_label()
        sublabel = env.next_label() if self.false else label
        self.cond.compare(n, sublabel)
        self.true.reduce(n)
        emit.jump(Cond.JR, f'.L{label}')
        emit.append_label(f'.L{sublabel}')
        self.false.branch_reduce(n, label)
        emit.append_label(f'.L{label}')
    def branch(self, n, root):
        sublabel = env.next_label()
        self.cond.compare(n, sublabel)
        self.true.reduce(n)
        emit.jump(Cond.JR, f'.L{root}')
        emit.append_label(f'.L{sublabel}')
        self.false.branch_reduce(n, root)

class Assign(Expr):
    def __init__(self, token, left, right):
        left.type == right.type, f'Line {token.line}: {left.type} != {right.type}'
        super().__init__(left.type, token)
        self.left, self.right = left, right      
    def reduce(self, n):
        self.generate(n)
        return regs[n]
    def generate(self, n):
        self.right.reduce(n)
        self.left.store(n)

class InitList(Expr):
    def __init__(self, token, left, right):
        super().__init__(left.type, token)
        self.left, self.right = left, right 
    def generate(self, n):
        self.left.address(n)
        for i in range(self.left.type.size):
            self.right[i].reduce(n+1)
            emit.store(regs[n+1], regs[n], i)        

class Block(UserList, Expr):
    def preview(self, n):
        emit.preview = env.preview = True
        for statement in self:
            statement.generate(n)
        emit.preview = env.preview = False
    def generate(self, n):
        for statement in self:
            statement.generate(n)

class Local(Expr):
    def store(self, n):
        return self.type.store(self, n, 'FP')
    def reduce(self, n):
        return self.type.reduce(self, n, 'FP')
    def address(self, n):
        return self.type.address(self, n, 'FP')

class Attr(Local):
    def store(self, n):
        return self.type.store(self, n, n+1)
    def reduce(self, n):
        return self.type.reduce(self, n, n)
    def address(self, n):
        return self.type.address(self, n, n)

class Glob(Local):
    def __init__(self, type, token):
        super().__init__(type, token)
        self.location = None
        self.init = None
    def store(self, n):
        return self.type.store(self, n, n+1)
    def reduce(self, n):
        return self.type.reduce(self, n, n)
    def address(self, n):
        emit.load_glob(regs[n], self.token.lexeme)
        return regs[n]
    def generate(self):
        self.type.glob(self)

class FuncBase(Expr):    
    def __init__(self, type, token, params):
        super().__init__(type, token)
        self.params = params
        
class Func(FuncBase):
    def address(self, n):
        emit.load_glob(regs[n], self.token.lexeme)
        return regs[n]      
    def call(self, n):
        emit.call(self.token.lexeme)

class FuncPtr(FuncBase):
    def reduce(self, n):
        Type.reduce(self, n, 'FP')
    def call(self, n):
        Type.reduce(self, n, 'FP')
        emit.call(regs[n])

class Params(UserList, Expr):
    pass
    
class Defn(Expr):
    def __init__(self, type, id, params, block, returns, calls, space):
        super().__init__(type, id)
        self.params, self.block, self.returns, self.calls, self.space = params, block, returns, calls, space
    def generate(self):
        regs.clear()
        env.begin_func(self)
        if self.type.size or self.returns: 
            env.return_label = env.next_label()
        self.block.preview(self.calls)
        push = list(map(Reg, range(bool(self.type.size), regs.max+1))) + [Reg.FP]
        for param in self.params:
            param.location += self.space + self.calls + len(push)
        emit.append_label(self.token.lexeme)
        #prologue
        emit.pushm(self.calls, *push)
        if self.space:
            emit.inst(Op.SUB, Reg.SP, self.space)
        emit.inst(Op.MOV, Reg.FP, Reg.SP)
        #body
        self.block.generate(self.calls)
        #epilogue
        if self.type.size or self.returns:
            emit.append_label(f'.L{env.return_label}')
        if self.calls and self.type.size:
            emit.inst(Op.MOV, Reg.A, regs[self.calls])
        emit.inst(Op.MOV, Reg.SP, Reg.FP)
        if self.space:
            emit.inst(Op.ADD, Reg.SP, self.space)
        emit.popm(self.calls, *push)
        if self.params:
            emit.inst(Op.ADD, Reg.SP, len(self.params))
        emit.ret()

class Main(Expr):
    def __init__(self, block, calls, space):
        self.block, self.calls, self.space = block, calls, space
    def generate(self):
        env.begin_func(self)
        emit.append_label('main')
        #prologue
        if self.space:
            emit.inst(Op.SUB, Reg.SP, self.space)
        emit.inst(Op.MOV, Reg.FP, Reg.SP)
        #body
        self.block.generate(self.calls)
        #epilogue
        emit.inst(Op.MOV, Reg.SP, Reg.FP)
        if self.space:
            emit.inst(Op.ADD, Reg.SP, self.space)
        emit.halt()

class Post(OpExpr):
    OP = {'++':Op.ADD,
          '--':Op.SUB}
    def __init__(self, op, postfix):
        assert postfix.type.cast(Type('int')), f'Line {op.line}: Cannot {op.lexeme} {postfix.type}' 
        super().__init__(postfix.type, op)
        self.postfix = postfix
    def reduce(self, n):
        self.generate(n)
        return regs[n]
    def generate(self, n):
        self.postfix.reduce(n)
        emit.inst3c(self.op, regs[n+1], regs[n], 1)
        self.postfix.store(n+1)

class Access(Expr):
    def __init__(self, type, token, postfix):
        super().__init__(type, token)
        self.postfix = postfix

class Dot(Access):
    def __init__(self, token, postfix, attr):
        super().__init__(attr.type, token, postfix)
        self.attr = attr
    def address(self, n):
        emit.inst(Op.ADD, self.postfix.address(n), self.attr.location)
        return regs[n]
    def store(self, n):
        self.postfix.address(n+1)
        return self.attr.store(n)
    def reduce(self, n):
        self.postfix.address(n)
        return self.attr.reduce(n)

class Arrow(Dot):
    def address(self, n):
        emit.inst(Op.ADD, self.postfix.reduce(n), self.attr.location)
        return regs[n] 
    def store(self, n):
        self.postfix.reduce(n+1)
        return self.attr.store(n)
    def reduce(self, n):
        self.postfix.reduce(n)
        return self.attr.reduce(n)

class SubScr(Access): 
    def __init__(self, token, postfix, sub):
        super().__init__(postfix.type.of, token, postfix)
        self.sub = sub
    def address(self, n):
        self.postfix.reduce(n)
        self.sub.reduce(n+1)
        if type(self.postfix.type) in [Array, Pointer] and self.postfix.type.of.size > 1:
            emit.inst(Op.MUL, regs[n+1], self.postfix.type.of.size)
        emit.inst(Op.ADD, regs[n], regs[n+1])
        return regs[n]
    def store(self, n):
        emit.store(regs[n], self.address(n+1))
        return regs[n]
    def reduce(self, n):
        emit.load(self.address(n), regs[n])
        return regs[n]

class Args(UserList, Expr):
    def generate(self, n):
        for arg in reversed(self):
            arg.reduce(n)
            emit.push(regs[n])

class Call(Expr):
    def __init__(self, func, args):
        for i, param in enumerate(func.params):
            assert param.type == args[i].type, f'Line {func.token.line}: Argument #{i+1} of {func.token.lexeme} {param.type} != {args[i].type}'
        super().__init__(func.type, func.token)
        self.func, self.args = func, args
    def reduce(self, n):
        self.generate(n)
        return regs[n]
    def generate(self, n):
        self.args.generate(n)
        self.func.call(n) #emit.call(self.func.token.lexeme)
        if self.func.params.variable and len(self.args) > len(self.func.params):
            emit.inst(Op.ADD, Reg.SP, len(self.args)-len(self.func.params))
        if n > 0:
            emit.inst(Op.MOV, regs[n], Reg.A)        

class Return(Expr):
    def __init__(self, token, expr):
        super().__init__(Void() if expr is None else expr.type, token)
        self.expr = expr
    def generate(self, n):
        assert env.defn.type == self.type, f'Line {self.token.line}: {env.defn.type} != {self.type} in {env.defn.token.lexeme}'       
        if self.expr:
            self.expr.reduce(n)
        emit.jump(Cond.JR, f'.L{env.return_label}')

class Statement(CNode):
    pass

class If(Statement):
    def __init__(self, cond, state):
        self.cond, self.true, self.false = cond, state, None
    def generate(self, n):
        env.if_jump_end = False
        label = env.next_label()
        sublabel = env.next_label() if self.false else label
        self.cond.compare(n, sublabel)
        self.true.generate(n)
        if self.false:
            if not (isinstance(self.true, Return) or (isinstance(self.true, Block) and self.true and isinstance(self.true[-1], Return))):
                emit.jump(Cond.JR, f'.L{label}')
                env.if_jump_end = True
            emit.append_label(f'.L{sublabel}')
            self.false.branch(n, label)
            if env.if_jump_end:
                emit.append_label(f'.L{label}')
        else:
            emit.append_label(f'.L{label}')
    def branch(self, n, root):
        sublabel = env.next_label()
        self.cond.compare(n, sublabel)
        self.true.generate(n)
        if self.false:
            if not (isinstance(self.true, Return) or (isinstance(self.true, Block) and self.true and isinstance(self.true[-1], Return))):
                emit.jump(Cond.JR, f'.L{root}')
                env.if_jump_end = True
            emit.append_label(f'.L{sublabel}')
            self.false.branch(n, root)

class Case(Statement):
    def __init__(self, const, statement):
        self.const, self.statement = const, statement

class Switch(Statement):
    def __init__(self, test):
        self.test, self.cases, self.default = test, [], None
    def generate(self, n):
        env.begin_loop()
        self.test.reduce(n)
        labels = []
        for case in self.cases:
            labels.append(env.next_label())
            emit.inst(Op.CMP, regs[n], case.const.num_reduce(n+1))
            emit.jump(Cond.JEQ, f'.L{labels[-1]}')
        if self.default:
            default = env.next_label()
            emit.jump(Cond.JR, f'.L{default}')
        else:
            emit.jump(Cond.JR, f'.L{env.loop.end()}')
        for i, case in enumerate(self.cases):
            emit.append_label(f'.L{labels[i]}')
            case.statement.generate(n)
        if self.default:
            emit.append_label(f'.L{default}')
            self.default.generate(n)
        emit.append_label(f'.L{env.loop.end()}')            
        env.end_loop()

class While(Statement):
    def __init__(self, cond, state):
        self.cond, self.state = cond, state
    def generate(self, n):
        env.begin_loop()
        emit.append_label(f'.L{env.loop.start()}')
        self.cond.compare(n, env.loop.end())
        self.state.generate(n)
        emit.jump(Cond.JR, f'.L{env.loop.start()}')
        emit.append_label(f'.L{env.loop.end()}')
        env.end_loop()

class Do(Statement):
    def __init__(self, state, cond):
        self.state, self.cond = state, cond
    def generate(self, n):
        env.begin_loop()
        emit.append_label(f'.L{env.loop.start()}')        
        self.state.generate(n)
        self.cond.compare_false(n, env.loop.start())
        emit.append_label(f'.L{env.loop.end()}')
        env.end_loop()

class For(While):
    def __init__(self, init, cond, step, state):
        super().__init__(cond, state)
        self.init, self.step = init, step
    def generate(self, n):
        self.init.generate(n)
        env.begin_loop()
        emit.append_label(f'.L{env.loop.start()}')
        self.cond.compare(n, env.loop.end())
        self.state.generate(n)
        self.step.generate(n)
        emit.jump(Cond.JR, f'.L{env.loop.start()}')
        emit.append_label(f'.L{env.loop.end()}')
        env.end_loop()

class Continue(Statement):
    def generate(self, n):
        emit.jump(Cond.JR, f'.L{env.loop.start()}')
        
class Break(Statement):
    def generate(self, n):
        emit.jump(Cond.JR, f'.L{env.loop.end()}')

class Goto(Statement):
    def __init__(self, target):
        self.target = target
    def generate(self, n):
        emit.jump(Cond.JR, self.target.lexeme)
        
class Label(Statement):
    def __init__(self, target):
        self.target = target
    def generate(self, n):
        emit.append_label(self.target.lexeme)

class Program(UserList, CNode):
    def generate(self):
        regs.clear()
        env.clear()
        emit.clear()
        for statement in self:
            statement.generate()
        return '\n'.join(emit.data+emit.asm)