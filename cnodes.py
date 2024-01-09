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
        if item == 'SP':
            return Reg.SP
        if item > Reg.E:
            print('\n'.join(emit.asm))
            raise SyntaxError('Not enough registers =(')
        self.max = max(self.max, item)
        return Reg(item)

regs = Regs()

class Frame(UserDict):
    def __init__(self):          
        self.size = 0
        super().__init__()
    def __setitem__(self, name, local):
        local.location = self.size
        self.size += local.type.size
        super().__setitem__(name, local)
        
class Environment:
    def clear(self):
        self.labels = 0
        self.loop = Loop()
        self.if_jump_end = False
        self.strings = []
    def begin_loop(self):
        self.loop.append((self.next_label(), self.next_label()))
    def end_loop(self):
        self.loop.pop()
    def next_label(self):
        label = self.labels
        self.labels += 1
        return label

env = Environment()

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
        self.asm.append(f'{name}: space {size}')
    def glob(self, name, value):
        self.asm.append(f'{name}: {value}')
    def pushm(self, lr, *regs):
        if lr:
            regs = (Reg.LR,) + regs
        if regs:
            self.func.insert(0, '  PUSH '+', '.join(reg.name for reg in regs))
    def popm(self, pc, *regs):
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
        self.asm.append(f'  {value}')
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
    def inst3(self, op, rd, rs, rs2):
        self.add(f'{op.name} {rd.name}, {rs.name}, {rs2.name}')
    def inst4(self, op, rd, rs, const4):
        self.add(f'{op.name} {rd.name}, {rs.name}, {const4}')
    def jump(self, cond, target):
        self.add(f'{cond.name} {target}')
    def halt(self):
        self.add('HALT')

emit = Emitter()

class CNode:
    def generate(self, n):
        pass

class Type(CNode):
    def __init__(self, type):
        self.type = type
        self.size = 0 if type == 'void' else 1
    def store(self, local, n, base):
        if local.location is None:
            emit.load_glob(regs[n+1], local.token.lexeme)
            emit.store(regs[n], regs[n+1])
        else:
            emit.store(regs[n], regs[base], local.location, local.token.lexeme)
        return regs[n]
    def address(self, local, n, base):
        emit.inst4(Op.ADD, regs[n], regs[base], local.location)
        return regs[n]
    def reduce(self, local, n, base):
        if local.location is None:
            emit.load_glob(regs[n], local.token.lexeme)
            emit.load(regs[n], regs[n])
        else:
            emit.load(regs[n], regs[base], local.location, local.token.lexeme)
        return regs[n]
    def ret(self, local, n, base):
        self.reduce(local, n, base)
    def glob(self, glob):
        if glob.init:
            emit.glob(glob.token.lexeme, glob.init.value)
        else:
            emit.space(glob.token.lexeme, 1)
    def __eq__(self, other):
        return type(other) is type(self)
    def __str__(self):
        return self.type

class Const(Type):
    def __init__(self, type):
        super().__init__(type)
        self.size = type.size
    def __eq__(self, other):
        return self.type == other or \
            (type(other) is Const and self.type == other.type)
    def __str__(self):
        return f'const {self.type}'
        
class Pointer(Type):
    def __init__(self, type):
        super().__init__(type)
        self.to = self.of = self.type
        self.size = 1
    def reduce(self, local, n, base):
        if local.location is None:
            emit.load_glob(regs[n], local.token.lexeme)
        else:
            emit.load(regs[n], regs[base], local.location, local.token.lexeme)
        return regs[n]
    def __eq__(self, other):
        return type(other) is Type and other.type == 'int' or \
            type(other) is Const and other.type.type == 'int' or \
                type(other) is Pointer and (self.to == other.to or \
                    type(other.to) is Type and other.to.type == 'void') or \
                        type(other) is Array and self.of == other.of
    def __str__(self):
        return f'{self.to}*'

class Struct(Type, Frame):
    def __init__(self, name):
        self.name = name
        self.size = 0
        self.data = {}
    def address(self, local, n, base):
        if local.location is None:
            emit.load_glob(regs[n], local.token.lexeme)
        else:
            emit.inst4(Op.ADD, regs[n], regs[base], local.location)
        return regs[n]
    def store(self, local, n, base):
        self.address(local, self.size, base)
        emit.storem(regs[0], self.size)
    def reduce(self, local, n, base):
        self.address(local, self.size, base)
        emit.loadm(regs[0], self.size)
        return regs[n]
    def ret(self, local, n, base):
        self.reduce(local, 0, base)
    def glob(self, glob):
        if glob.init:
            datas = [expr.data() for expr in glob.init]
            emit.asm.append(f'{glob.token.lexeme}:')
            for data in datas:
                emit.data(data)
        else:
            emit.space(glob.token.lexeme, self.size)       
    def __eq__(self, other):
        return type(other) is Struct and self.name == other.name or \
            other == 'list'
    def __str__(self):
        return f'struct {self.name}'
    
class Array(Type):
    def __init__(self, of, length):
        self.size = of.size * length.value
        self.of = of
        self.length = length.value    
    def address(self, local, n, base):
        if local.location is None:
            emit.load_glob(regs[n], local.token.lexeme)
        else:
            emit.inst4(Op.ADD, regs[n], regs[base], local.location)
        return regs[n]
    def store(self, local, n, base):
        self.address(local, self.size, base)
        emit.storem(regs[0], self.size)
    def reduce(self, local, n, base):
        return self.address(local, n, base)
    def glob(self, glob):
        if glob.init:
            datas = [expr.data() for expr in glob.init]
            emit.asm.append(f'{glob.token.lexeme}:')
            for data in datas:
                emit.data(data)
        else:
            emit.space(glob.token.lexeme, self.size)
    def __eq__(self, other):
        return type(other) is Array and self.of == other.of or \
            other == 'list'
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
    def ret(self, n):
        self.reduce(n)
    def num_reduce(self, n):
        return self.reduce(n)
    
class NumBase(Expr):
    def __init__(self, token):
        super().__init__(Const(Type('int')), token)
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
        super().__init__(Const(Type('char')), token)
    def data(self):
        return self.token.lexeme
    def reduce(self, n):
        emit.imm(regs[n], self.data())
        return regs[n]

class String(Expr):
    def __init__(self, token):
        super().__init__(Pointer(Const(Type('char'))), token)
        self.value = f'"{token.lexeme[1:-1]}\\0"'
    def data(self):
        if self.value not in env.strings:
            env.strings.append(self.value)
            emit.glob(f'.S{env.strings.index(self.value)}', self.value)
        return f'.S{env.strings.index(self.value)}'
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
        assert unary.type == Type('int'), f'Line {op.line_no}: Cannot {op.lexeme} {unary.type}'
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
        assert hasattr(unary.type, 'to'), f'Line {token.line_no}: Cannot {token.lexeme} {unary.type}'
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
        assert type == cast.type, f'Line {token.line_no}: Cannot cast {cast.type} to {type}'
        super().__init__(type, token)
        self.cast = cast
    def reduce(self, n):
        return self.cast.reduce(n)
    
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
        emit.labels.append(f'.L{sublabel}')
        emit.inst(Op.MOV, Reg(n), 1)
        emit.labels.append(f'.L{label}')
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
          '&=':Op.AND,}
    def __init__(self, op, left, right):
        assert left.type == right.type, f'Line {op.line_no}: Cannot {left.type} {op.lexeme} {right.type}'
        super().__init__(left.type, op)
        self.left, self.right = left, right
    def reduce(self, n):
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
        emit.labels.append(f'.L{sublabel}')
        emit.inst(Op.MOV, Reg(n), 0)
        emit.labels.append(f'.L{label}')
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
            emit.labels.append(f'.L{sublabel}')

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
        emit.labels.append(f'.L{sublabel}')
        self.false.branch_reduce(n, label)
        emit.labels.append(f'.L{label}')
    def branch(self, n, root):
        sublabel = env.next_label()
        self.cond.compare(n, sublabel)
        self.true.reduce(n)
        emit.jump(Cond.JR, f'.L{root}')
        emit.labels.append(f'.L{sublabel}')
        self.false.branch_reduce(n, root)

class Assign(Expr):
    def __init__(self, token, left, right):
        assert left.type == right.type, f'Line {token.line_no}: {left.type} != {right.type}'
        super().__init__(left.type, token)
        self.left, self.right = left, right
    def analyze(self, n):
        self.right.analyze(n)
        self.left.analyze_store(n)        
    def reduce(self, n):
        self.generate(n)
        return regs[n]
    def generate(self, n):
        self.right.reduce(n)
        self.left.store(n)
    
class Block(UserList, Expr):
    def generate(self, n):
        for statement in self:
            statement.generate(n)

class Local(Expr):
    def store(self, n):
        return self.type.store(self, n, 'SP')
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
    def ret(self, n):
        self.type.ret(self, n, n)
    def generate(self):
        self.type.glob(self)
        
class Func(Local):
    def __init__(self, type, token, params):
        super().__init__(type, token)
        self.params = params

class List(UserList, Expr):
    def __init__(self):
        self.type = 'list'
        super().__init__()
    def reduce(self, n):
        for i, expr in enumerate(self):
            expr.reduce(i)
        return regs[0]

class Params(UserList, Expr):
    def generate(self):
        if len(self) > 2 or self.va_list:
            emit.store(Reg.A, Reg.SP, 0, self[0].token.lexeme)
            for i, param in enumerate(self[1:]):
                emit.load(Reg.C, Reg.B, i)
                emit.store(Reg.C, Reg.SP, i+1, param.token.lexeme)
        else:
            for i, param in enumerate(self[:2]):
                emit.store(regs[i], Reg.SP, i, param.token.lexeme)
    
class Defn(Expr):
    def __init__(self, type, id, params, block, max_args, space, stack):
        super().__init__(type, id)
        self.params, self.block, self.max_args, self.space, self.stack = params, block, max_args, space, stack
    def generate(self):
        emit.begin_func()
        regs.clear()
        env.space = self.space
        if self.space+self.stack:
            emit.inst(Op.SUB, Reg.SP, self.space+self.stack)
        if self.type.size: 
            env.return_label = env.next_label()
        if self.params.va_list:
            self.params.va_list.store(Reg.C)            
        self.params.generate()
        self.block.generate(0 if self.max_args is None else min(self.max_args, 2))
        if self.type.size: 
            emit.func.append(f'.L{env.return_label}:')
        if type(self.type) is not Struct and self.max_args is not None and self.max_args > 0 and self.type.size:
            emit.inst(Op.MOV, Reg.A, regs[min(self.max_args, 2)])
        if self.space+self.stack:
            emit.inst(Op.ADD, Reg.SP, self.space+self.stack)
        push = list(map(Reg, range(max(len(self.params), self.type.size), regs.max+1))) 
        emit.pushm(self.max_args is not None, *push)
        emit.popm(self.max_args is not None, *push)
        emit.func.insert(0, f'{self.token.lexeme}:')
        if self.max_args is None:
            emit.ret()
        emit.end_func()

class Main(Expr):
    def __init__(self, block, space, stack):
        self.block, self.space, self.stack = block, space, stack
    def generate(self):
        emit.begin_func()
        env.space = self.space
        if self.space+self.stack:
            emit.inst(Op.SUB, Reg.SP, self.space+self.stack)
        self.block.generate(0)
        if self.space+self.stack:
            emit.inst(Op.ADD, Reg.SP, self.space+self.stack)
        emit.halt()
        emit.end_func()

class Post(OpExpr):
    OP = {'++':Op.ADD,
          '--':Op.SUB}
    def __init__(self, op, postfix):
        assert postfix.type == Type('int'), f'Line {op.line_no}: Cannot {op.lexeme} {postfix.type}' 
        super().__init__(postfix.type, op)
        self.postfix = postfix
    def reduce(self, n):
        self.generate(n)
        return regs[n]
    def generate(self, n):
        self.postfix.reduce(n)
        emit.inst4(self.op, regs[n+1], regs[n], 1)
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
    def generate(self, n, is_var):
        if len(self) > 2 or is_var:
            # self[0].reduce(Reg.D if is_var else Reg.A)
            emit.inst4(Op.ADD, Reg.B, Reg.SP, env.space if env.space < 7 else print("WARNING: too much stack space"))
            for i, arg in enumerate(self[1:]):
                arg.reduce(Reg.C)
                emit.store(Reg.C, Reg.B, i)
            self[0].reduce(Reg.C)
            emit.inst(Op.MOV, Reg.A, Reg.C)
        else:
            for i, arg in enumerate(self):
                arg.reduce(n+i)
            if n > 0:
                for i, arg in enumerate(self[:2]):
                    emit.inst(Op.MOV, regs[i], regs[n+i])                

class Call(Expr):
    def __init__(self, func, args):
        if len(func.params) == len(args):
            for i, arg in enumerate(args):
                pass#assert func.params[i] == arg.type, f'Line {func.token.line_no}: Argument #{i+1} of {func.token.lexeme} {func.params[i]} != {arg.type}'
        else:
            pass #TODO error handle
        super().__init__(func.type, func.token)
        self.func, self.args = func, args
    def reduce(self, n):
        self.generate(n)
        return regs[n]
    def generate(self, n):
        self.args.generate(n, self.func.params.va_list)
        if self.func.params.va_list:
            emit.inst4(Op.ADD, Reg.C, Reg.B, len(self.func.params) - 1)
        emit.call(self.func.token.lexeme)
        if n > 0 and type(self.func.type) is not Struct:
            emit.inst(Op.MOV, regs[n], Reg.A)

class Return(Expr):
    def __init__(self, token):
        super().__init__(Type('void'), token)
        self.expr = None
    def generate(self, n):
        # TODO assert type == func.type, f'{self.expr.type} != {func.type} in {env.func.id.name}'       
        if self.expr:
            self.expr.ret(n)
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
            emit.labels.append(f'.L{sublabel}')
            self.false.branch(n, label)
            if env.if_jump_end:
                emit.labels.append(f'.L{label}')
        else:
            emit.labels.append(f'.L{label}')
        if env.if_jump_end:
            emit.labels.append(f'.L{label}')
    def branch(self, n, root):
        sublabel = env.next_label()
        self.cond.compare(n, sublabel)
        self.true.generate(n)
        if self.false:
            if not (isinstance(self.true, Return) or (isinstance(self.true, Block) and self.true and isinstance(self.true[-1], Return))):
                emit.jump(Cond.JR, f'.L{root}')
                env.if_jump_end = True
            emit.labels.append(f'.L{sublabel}')
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
            # case.const.compare(n, labels[-1])
            emit.inst(Op.CMP, regs[n], case.const.num_reduce(n+1))
            emit.jump(Cond.JEQ, f'.L{labels[-1]}')
        if self.default:
            default = env.next_label()
            emit.jump(Cond.JR, f'.L{default}')
        else:
            emit.jump(Cond.JR, f'.L{env.loop.end()}')
        for i, case in enumerate(self.cases):
            emit.labels.append(f'.L{labels[i]}')
            case.statement.generate(n)
        if self.default:
            emit.labels.append(f'.L{default}')
            self.default.generate(n)
        emit.labels.append(f'.L{env.loop.end()}')            
        env.end_loop()

class While(Statement):
    def __init__(self, cond, state):
        self.cond, self.state = cond, state
    def generate(self, n):
        env.begin_loop()
        emit.labels.append(f'.L{env.loop.start()}')
        self.cond.compare(n, env.loop.end())
        self.state.generate(n)
        emit.jump(Cond.JR, f'.L{env.loop.start()}')
        emit.labels.append(f'.L{env.loop.end()}')
        env.end_loop()

class Do(Statement):
    def __init__(self, state, cond):
        self.state, self.cond = state, cond
    def generate(self, n):
        env.begin_loop()
        emit.labels.append(f'.L{env.loop.start()}')        
        self.state.generate(n)
        self.cond.compare_false(n, env.loop.start())
        emit.labels.append(f'.L{env.loop.end()}')
        env.end_loop()

class For(While):
    def __init__(self, init, cond, step, state):
        super().__init__(cond, state)
        self.init, self.step = init, step
    def generate(self, n):
        self.init.generate(n)
        env.begin_loop()
        emit.labels.append(f'.L{env.loop.start()}')
        self.cond.compare(n, env.loop.end())
        self.state.generate(n)
        self.step.generate(n)
        emit.jump(Cond.JR, f'.L{env.loop.start()}')
        emit.labels.append(f'.L{env.loop.end()}')
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
        emit.labels.append(self.target.lexeme)

class Program(UserList, CNode):
    def generate(self):
        regs.clear()
        env.clear()
        emit.clear()
        for statement in self:
            statement.generate()
        return '\n'.join(emit.asm)