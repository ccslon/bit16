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
            raise SyntaxError('Not enough registers =(')
        self.max = max(self.max, item)
        return Reg(item)

regs = Regs()

class Frame(UserDict):
    def __init__(self):
        super().__init__()
        self.size = 0
    def __setitem__(self, name, obj):
        obj.location = self.size
        self.size += obj.type.size
        super().__setitem__(name, obj)

class Visitor:
    def __init__(self):
        self.clear()
    def clear(self):
        self.n_labels = 0
        self.if_jump_end = False
        self.loop = Loop()
    def begin_func(self, defn):
        if defn.type.size or defn.returns:
            self.return_label = self.next_label()
        self.defn = defn
    def begin_loop(self):
        self.loop.append((self.next_label(), self.next_label()))
    def end_loop(self):
        self.loop.pop()
    def next_label(self):
        label = self.n_labels
        self.n_labels += 1
        return label
    def append_label(self, label):
        pass
    def string(self, string):
        pass
    def add(self, asm):
        pass
    def space(self, name, size):
        pass
    def glob(self, name, value):
        pass
    def datas(self, label, datas):
        pass
    def push(self, reg):
        pass
    def pop(self, reg):
        pass
    def pushm(self, calls, *regs):
        pass
    def popm(self, calls, *regs):
        pass
    def call(self, proc):
        pass
    def ret(self):
        pass
    def load_glob(self, rd, name):
        pass
    def load(self, rd, rb, offset=None, name=None):
        pass
    def store(self, rd, rb, offset=None, name=None):
        pass
    def imm(self, rd, value):
        pass
    def loadm(self, rd, size):
        pass
    def storem(self, rd, size):
        pass
    def inst(self, op, rd, src):
        pass
    def inst3(self, op, rd, rs, const4):
        pass
    def jump(self, cond, target):
        pass
    def halt(self):
        pass

class Emitter(Visitor):
    def clear(self):
        super().clear()
        self.labels = []
        self.asm = []
        self.data = []
        self.strings = []
    def append_label(self, label):
        self.labels.append(label)
    def string(self, string):
        if string not in self.strings:
            self.strings.append(string)
            self.glob(f'.S{self.strings.index(string)}', string)
        return f'.S{self.strings.index(string)}'
    def add(self, asm):
        for label in self.labels:
            self.asm.append(f'{label}:')
        self.asm.append(f'  {asm}')
        self.labels.clear()
    def space(self, name, size):
        self.data.append(f'{name}: space {size}')
    def glob(self, name, value):
        self.data.append(f'{name}: {value}')
    def datas(self, label, datas):
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
    def load(self, rd, rb, offset=None, name=None):
        self.add(f'LD {rd.name}, [{rb.name}'+(f', {offset}' if offset is not None else '')+']'+(f' ; {name}' if name else ''))
    def store(self, rd, rb, offset=None, name=None):
        self.add(f'LD [{rb.name}'+(f', {offset}' if offset is not None else '')+f'], {rd.name}'+(f' ; {name}' if name else ''))
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
            if isinstance(src, Reg):
                self.add(f'{op.name} {rd.name}, {src.name}')
            else:
                self.add(f'{op.name} {rd.name}, {src}')
    def inst3(self, op, rd, rs, const):
        self.add(f'{op.name} {rd.name}, {rs.name}, {const}')
    def jump(self, cond, target):
        self.add(f'{cond.name} {target}')
    def halt(self):
        self.add('HALT')

class CNode:
    def generate(self, vstr, n):
        pass

class Void(CNode):
    def __init__(self):
        self.size = 0
    def __eq__(self, other):
        return type(other) is Void
    def __str__(self):
        return 'void'

class Type(CNode):
    def __init__(self):
        self.const = False
    @staticmethod
    def address(vstr, n, local, base):
        vstr.inst3(Op.ADD, regs[n], regs[base], local.location)
        return regs[n]

class Word(Type):
    def __init__(self, type, unsigned=False):
        super().__init__()
        self.type = type
        self.unsigned = unsigned
        self.size = 1
    def is_unsigned(self):
        return self.unsigned
    @staticmethod
    def store(vstr, n, local, base):
        if local.location is None:
            vstr.load_glob(regs[n+1], local.token.lexeme)
            vstr.store(regs[n], regs[n+1])
        else:
            vstr.store(regs[n], regs[base], local.location, local.token.lexeme)
        return regs[n]
    @staticmethod
    def reduce(vstr, n, local, base):
        if local.location is None:
            vstr.load_glob(regs[n], local.token.lexeme)
            vstr.load(regs[n], regs[n])
        else:
            vstr.load(regs[n], regs[base], local.location, local.token.lexeme)
        return regs[n]
    @staticmethod
    def glob(vstr, glob):
        if glob.init:
            vstr.glob(glob.token.lexeme, glob.init.data(vstr))
        else:
            vstr.space(glob.token.lexeme, glob.type.size)
    def cast(self, other):
        return isinstance(other, Word)
    def __eq__(self, other):
        return type(other) is Word
    def __str__(self):
        return self.type

class Pointer(Word):
    def __init__(self, type):
        super().__init__(type)
        self.to = self.of = self.type
        self.unsigned = True
        self.size = 1
    def cast(self, other):
        return isinstance(other, Word)
    def __eq__(self, other):
        return type(other) is Pointer and (self.to == other.to \
                                           or type(self.to) is Void \
                                           or type(other.to) is Void) \
            or type(other) is Array and self.of == other.of
    def __str__(self):
        return f'{self.to}*'

class Struct(Frame, Type):
    def __init__(self, name):
        super().__init__()
        self.const = False
        self.name = name
    @staticmethod
    def store(vstr, n, local, base):
        Struct.address(vstr, n+1, local, base)
        for i in range(local.type.size):
            vstr.load(regs[n+2], regs[n], i)
            vstr.store(regs[n+2], regs[n+1], i)
    @staticmethod
    def reduce(vstr, n, local, base):
        return Struct.address(vstr, n, local, base)
    @staticmethod
    def glob(vstr, glob):
        if glob.init:
            vstr.datas(glob.token.lexeme, [expr.data(vstr) for expr in glob.init])
        else:
            vstr.space(glob.token.lexeme, glob.type.size)
    def cast(self, other):
        return self == other
    def __eq__(self, other):
        return type(other) is Struct and self.name == other.name
    def __str__(self):
        return f'struct {self.name}'

class Union(UserDict, Word): #TODO
    def __init__(self, name):
        super().__init__()
        self.const = False
        self.size = -1
        self.name = name
    def __setitem__(self, name, attr):
        attr.location = 0
        self.size = max(self.size, attr.type.size)
        super().__setitem__(name, attr)

class Array(Type):
    def __init__(self, of, length):
        super().__init__()
        self.size = of.size * length.value
        self.of = of
        self.length = length.value
    @staticmethod
    def address(vstr, n, local, base):
        if local.location is None:
            vstr.load_glob(regs[n], local.token.lexeme)
        else:
            Word.address(vstr, n, local, base)
        return regs[n]
    @staticmethod
    def reduce(vstr, n, local, base):
        return Array.address(vstr, n, local, base)
    @staticmethod
    def glob(vstr, glob):
        if glob.init:
            vstr.datas(glob.token.lexeme, [expr.data(vstr) for expr in glob.init])
        else:
            vstr.space(glob.token.lexeme, glob.type.size)
    def cast(self, other):
        return self == other
    def __eq__(self, other):
        return isinstance(other, Array | Pointer) and self.of == other.of
    def __str__(self):
        return f'{self.of}[]'

class Func(Type):
    def __init__(self, ret, params, variable):
        self.ret, self.params, self.variable = ret, params, variable
        self.size = ret.size
    def cast(self, other):
        return False
    def __eq__(self, other):
        return type(other) is Func and self.ret == other.ret #TODO
    def __str__(self):
        return f'{self.ret}('+','.join(map(str, self.params))+')'

class Expr(CNode):
    def __init__(self, type, token):
        self.type = type
        self.token = token
    def branch_reduce(self, vstr, n , _):
        self.reduce(vstr, n)
    def branch(self, vstr, n, _):
        self.generate(vstr, n)
    def compare(self, vstr, n, label):
        vstr.inst(Op.CMP, self.reduce(vstr, n), 0)
        vstr.jump(Cond.JEQ, f'.L{label}')
    def compare_false(self, vstr, n, label):
        vstr.inst(Op.CMP, self.reduce(vstr, n), 0)
        vstr.jump(Cond.JNE, f'.L{label}')
    def num_reduce(self, vstr, n):
        return self.reduce(vstr, n)
    def is_unsigned(self):
        return self.type.is_unsigned()

class NumBase(Expr):
    def __init__(self, token):
        super().__init__(Word('int'), token)
    def data(self, vstr):
        return self.value
    def reduce(self, vstr, n):
        if -16 <= self.value < 256:
            vstr.inst(Op.MOV, regs[n], self.value)
        else:
            vstr.imm(regs[n], self.value)
        return regs[n]
    def num_reduce(self, vstr, n):
        if -16 <= self.value < 16:
            return self.value
        elif 0 <= self.value < 256:
            vstr.inst(Op.MOV, regs[n], self.value)
        else:
            vstr.imm(regs[n], self.value)
        return regs[n]

class EnumConst(NumBase):
    def __init__(self, token, value):
        super().__init__(token)
        self.value = value

class Num(NumBase):
    def __init__(self, token):
        super().__init__(token)
        if token.lexeme.startswith('0x'):
            self.value = int(token.lexeme, base=16)
        elif token.lexeme.startswith('0b'):
            self.value = int(token.lexeme, base=2)
        else:
            self.value = int(token.lexeme)

class NegNum(Num):
    def __init__(self, token):
        super().__init__(token)
        self.value = -self.value

class SizeOf(NumBase):
    def __init__(self, token, type):
        super().__init__(token)
        self.value = type.size

class Char(Expr):
    def __init__(self, token):
        super().__init__(Word('char'), token)
    def data(self):
        return self.token.lexeme
    def reduce(self, vstr, n):
        vstr.inst(Op.MOV, regs[n], self.data())
        return regs[n]
    def num_reduce(self, vstr, n):
        return self.data()

class String(Expr):
    def __init__(self, token):
        super().__init__(Pointer(Word('char')), token)
        self.value = f'"{token.lexeme[1:-1]}\\0"'
    def data(self, vstr):
        return vstr.string(self.value)
    def reduce(self, vstr, n):
        vstr.load_glob(regs[n], self.data(vstr))
        return regs[n]

class OpExpr(Expr):
    def __init__(self, type, op):
        super().__init__(type, op)
        self.op = self.OP[op.lexeme]

class Unary(OpExpr):
    OP = {'-':Op.NEG,
          '~':Op.NOT}
    def __init__(self, op, unary):
        assert unary.type.cast(Word('int')), f'Line {op.line}: Cannot {op.lexeme} {unary.type}'
        super().__init__(unary.type, op)
        self.unary = unary
    def reduce(self, vstr, n):
        vstr.inst(self.op, self.unary.reduce(vstr, n), Reg.A)
        return regs[n]

class Pre(Unary):
    OP = {'++':Op.ADD,
          '--':Op.SUB}
    def reduce(self, vstr, n):
        self.generate(vstr, n)
        return regs[n]
    def generate(self, vstr, n):
        self.unary.reduce(vstr, n)
        vstr.inst(self.op, regs[n], 1)
        self.unary.store(vstr, n)

class AddrOf(Expr):
    def __init__(self, token, unary):
        super().__init__(Pointer(unary.type), token)
        self.unary = unary
    def reduce(self, vstr, n):
        return self.unary.address(vstr, n)

class Deref(Expr):
    def __init__(self, token, unary):
        assert hasattr(unary.type, 'to'), f'Line {token.line}: Cannot {token.lexeme} {unary.type}'
        super().__init__(unary.type.to, token)
        self.unary = unary
    def store(self, vstr, n):
        self.unary.reduce(vstr, n+1)
        vstr.store(regs[n], regs[n+1])
    def reduce(self, vstr, n):
        self.unary.reduce(vstr, n)
        vstr.load(regs[n], regs[n])
        return regs[n]
    def call(self, vstr, n):
        self.unary.call(vstr, n)

class Cast(Expr):
    def __init__(self, type, token, cast):
        assert type.cast(cast.type), f'Line {token.line}: Cannot cast {cast.type} to {type}'
        super().__init__(type, token)
        self.cast = cast
    def reduce(self, vstr, n):
        return self.cast.reduce(vstr, n)
    def data(self, vstr):
        return self.cast.data(vstr)

class Not(Expr):
    def __init__(self, token, unary):
        super().__init__(unary.type, token)
        self.unary = unary
    def compare(self, vstr, n, label):
        vstr.inst(Op.CMP, self.unary.reduce(vstr, n), 0)
        vstr.jump(Cond.JNE, f'.L{label}')
    def compare_false(self, vstr, n, label):
        vstr.inst(Op.CMP, self.unary.reduce(vstr, n), 0)
        vstr.jump(Cond.JEQ, f'.L{label}')
    def reduce(self, vstr, n):
        label = vstr.next_label()
        sublabel = vstr.next_label()
        self.unary.compare(vstr, n, sublabel)
        vstr.inst(Op.MOV, regs[n], 0)
        vstr.jump(Cond.JR, f'.L{label}')
        vstr.append_label(f'.L{sublabel}')
        vstr.inst(Op.MOV, regs[n], 1)
        vstr.append_label(f'.L{label}')
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
          '/': Op.DIV,
          '/=':Op.DIV,
          '%': Op.MOD,
          '%=':Op.MOD}
    def __init__(self, op, left, right):
        assert left.type.cast(right.type), f'Line {op.line}: Cannot {left.type} {op.lexeme} {right.type}'
        super().__init__(left.type, op)
        self.left, self.right = left, right
    def is_unsigned(self):
        return self.left.is_unsigned() or self.right.is_unsigned()
    def reduce(self, vstr, n):
        vstr.inst(self.op, self.left.reduce(vstr, n), self.right.num_reduce(vstr, n+1))
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
    UOP = {'>': Cond.JHI,
           '<': Cond.JLO,
           '>=':Cond.JHS,
           '<=':Cond.JLS}
    UINV = {'>': Cond.JLS,
            '<': Cond.JHS,
            '>=':Cond.JLO,
            '<=':Cond.JHI}
    def __init__(self, op, left, right):
        super().__init__(op, left, right)
        if self.is_unsigned():
            self.op = self.UOP.get(op.lexeme, self.OP[op.lexeme])
            self.inv = self.UINV.get(op.lexeme, self.INV[op.lexeme])
        else:
            self.op = self.OP[op.lexeme]
            self.inv = self.INV[op.lexeme]
    def compare(self, vstr, n, label):
        vstr.inst(Op.CMP, self.left.reduce(vstr, n), self.right.num_reduce(vstr, n+1))
        vstr.jump(self.inv, f'.L{label}')
    def compare_false(self, vstr, n, label):
        vstr.inst(Op.CMP, self.left.reduce(vstr, n), self.right.num_reduce(vstr, n+1))
        vstr.jump(self.op, f'.L{label}')
    def reduce(self, vstr, n):
        label = vstr.next_label()
        sublabel = vstr.next_label()
        self.compare_false(vstr, n, label)
        vstr.inst(Op.MOV, regs[n], 0)
        vstr.jump(Cond.JR, f'.L{sublabel}')
        vstr.append_label(f'.L{label}')
        vstr.inst(Op.MOV, regs[n], 1)
        vstr.append_label(f'.L{sublabel}')
        return regs[n]

class Logic(Binary):
    OP = {'&&':Op.AND,
          '||':Op.OR}
    def compare(self, vstr, n, label):
        if self.op == Op.AND:
            vstr.inst(Op.CMP, self.left.reduce(vstr, n), 0)
            vstr.jump(Cond.JEQ, f'.L{label}')
            vstr.inst(Op.CMP, self.right.reduce(vstr, n), 0)
            vstr.jump(Cond.JEQ, f'.L{label}')
        elif self.op == Op.OR:
            sublabel = vstr.next_label()
            vstr.inst(Op.CMP, self.left.reduce(vstr, n), 0)
            vstr.jump(Cond.JNE, f'.L{sublabel}')
            vstr.inst(Op.CMP, self.right.reduce(vstr, n), 0)
            vstr.jump(Cond.JEQ, f'.L{label}')
            vstr.append_label(f'.L{sublabel}')
    def compare_false(self, vstr, n, label): #TODO
        pass

class Condition(Expr):
    def __init__(self, cond, true, false):
        self.type = true.type
        self.cond, self.true, self.false = cond, true, false
    def reduce(self, vstr, n):
        vstr.if_jump_end = False
        label = vstr.next_label()
        sublabel = vstr.next_label() if self.false else label
        self.cond.compare(vstr, n, sublabel)
        self.true.reduce(vstr, n)
        vstr.jump(Cond.JR, f'.L{label}')
        vstr.append_label(f'.L{sublabel}')
        self.false.branch_reduce(vstr, n, label)
        vstr.append_label(f'.L{label}')
    def branch(self, vstr, n, root):
        sublabel = vstr.next_label()
        self.cond.compare(vstr, n, sublabel)
        self.true.reduce(vstr, n)
        vstr.jump(Cond.JR, f'.L{root}')
        vstr.append_label(f'.L{sublabel}')
        self.false.branch_reduce(vstr, n, root)

class InitAssign(Expr):
    def __init__(self, token, left, right):
        assert left.type == right.type, f'Line {token.line}: {left.type} != {right.type}'
        super().__init__(left.type, token)
        self.left, self.right = left, right
    def reduce(self, vstr, n):
        self.generate(vstr, n)
        return regs[n]
    def generate(self, vstr, n):
        self.right.reduce(vstr, n)
        self.left.store(vstr, n)

class Assign(InitAssign):
    def __init__(self, token, left, right):
        assert not left.type.const, 'Line {token.line}: Left is const'
        super().__init__(token, left, right)
        
class InitListAssign(Expr):
    def __init__(self, token, left, right):
        super().__init__(left.type, token)
        self.left, self.right = left, right
    def generate(self, vstr, n):
        self.left.address(vstr, n)
        for i in range(self.left.type.size):
            self.right[i].reduce(vstr, n+1)
            vstr.store(regs[n+1], regs[n], i)

class Block(UserList, Expr):
    def generate(self, vstr, n):
        for statement in self:
            statement.generate(vstr, n)

class Local(Expr):
    def store(self, vstr, n):
        return self.type.store(vstr, n, self, 'FP')
    def reduce(self, vstr, n):
        return self.type.reduce(vstr, n, self, 'FP')
    def address(self, vstr, n):
        return self.type.address(vstr, n, self, 'FP')
    def call(self, vstr, n):
        Word.reduce(vstr, n, self, 'FP')
        vstr.call(regs[n])

class Attr(Local):
    def store(self, vstr, n):
        return self.type.store(vstr, n, self, n+1)
    def reduce(self, vstr, n):
        return self.type.reduce(vstr, n, self, n)
    def address(self, vstr, n):
        return self.type.address(vstr, n, self, n)
    def call(self, vstr, n):
        Word.reduce(vstr, n, self, n)
        vstr.call(regs[n])

class Glob(Local):
    def __init__(self, type, token):
        super().__init__(type, token)
        self.location = None
        self.init = None
    def store(self, vstr, n):
        return self.type.store(vstr, n, self, n+1)
    def reduce(self, vstr, n):
        return self.type.reduce(vstr, n, self, n)
    def address(self, vstr, n):
        vstr.load_glob(regs[n], self.token.lexeme)
        return regs[n]
    def generate(self, vstr):
        self.type.glob(vstr, self)
    def call(self, vstr, n):
        vstr.call(self.token.lexeme)

class Defn(Expr):
    def __init__(self, type, id, params, block, returns, calls, space):
        super().__init__(type, id)
        self.params, self.block, self.returns, self.calls, self.space = params, block, returns, calls, space
    def generate(self, vstr):
        regs.clear()
        preview = Visitor()
        preview.begin_func(self)
        self.block.generate(preview, self.calls)
        # self.block.preview(self.calls)
        push = list(map(Reg, range(bool(self.type.size), regs.max+1))) + [Reg.FP]
        for param in self.params:
            param.location += self.space + self.calls + len(push)

        vstr.begin_func(self)
        #start
        vstr.append_label(self.token.lexeme)
        #prologue
        vstr.pushm(self.calls, *push)
        if self.space:
            vstr.inst(Op.SUB, Reg.SP, self.space)
        vstr.inst(Op.MOV, Reg.FP, Reg.SP)
        #body
        self.block.generate(vstr, self.calls)
        #epilogue
        if self.type.size or self.returns:
            vstr.append_label(f'.L{vstr.return_label}')
        if self.calls and self.type.size:
            vstr.inst(Op.MOV, Reg.A, regs[self.calls])
        vstr.inst(Op.MOV, Reg.SP, Reg.FP)
        if self.space:
            vstr.inst(Op.ADD, Reg.SP, self.space)
        vstr.popm(self.calls, *push)
        if self.params:
            vstr.inst(Op.ADD, Reg.SP, len(self.params))
        vstr.ret()

class Post(OpExpr):
    OP = {'++':Op.ADD,
          '--':Op.SUB}
    def __init__(self, op, postfix):
        assert postfix.type.cast(Word('int')), f'Line {op.line}: Cannot {op.lexeme} {postfix.type}'
        super().__init__(postfix.type, op)
        self.postfix = postfix
    def reduce(self, vstr, n):
        self.generate(vstr, n)
        return regs[n]
    def generate(self, vstr, n):
        self.postfix.reduce(vstr, n)
        vstr.inst3(self.op, regs[n+1], regs[n], 1)
        self.postfix.store(vstr, n+1)

class Access(Expr):
    def __init__(self, type, token, postfix):
        super().__init__(type, token)
        self.postfix = postfix

class Dot(Access):
    def __init__(self, token, postfix, attr):
        super().__init__(attr.type, token, postfix)
        self.attr = attr
    def address(self, vstr, n):
        vstr.inst(Op.ADD, self.postfix.address(vstr, n), self.attr.location)
        return regs[n]
    def store(self, vstr, n):
        self.postfix.address(vstr, n+1)
        return self.attr.store(vstr, n)
    def reduce(self, vstr, n):
        self.postfix.address(vstr, n)
        return self.attr.reduce(vstr, n)
    def call(self, vstr, n):
        self.postfix.address(vstr, n)
        self.attr.call(vstr, n)

class Arrow(Dot):
    def address(self, vstr, n):
        vstr.inst(Op.ADD, self.postfix.reduce(vstr, n), self.attr.location)
        return regs[n]
    def store(self, vstr, n):
        self.postfix.reduce(vstr, n+1)
        return self.attr.store(vstr, n)
    def reduce(self, vstr, n):
        self.postfix.reduce(vstr, n)
        return self.attr.reduce(vstr, n)
    def call(self, vstr, n):
        self.postfix.reduce(vstr, n)
        self.attr.call(vstr, n)

class SubScr(Access):
    def __init__(self, token, postfix, sub):
        super().__init__(postfix.type.of, token, postfix)
        self.sub = sub
    def address(self, vstr, n):
        self.postfix.reduce(vstr, n)
        if type(self.postfix.type) in [Array, Pointer] and self.postfix.type.of.size > 1:
            self.sub.reduce(vstr, n+1)
            vstr.inst(Op.MUL, regs[n+1], self.postfix.type.of.size)
            vstr.inst(Op.ADD, regs[n], regs[n+1])
        else:
            vstr.inst(Op.ADD, regs[n], self.sub.num_reduce(vstr, n+1))
        return regs[n]
    def store(self, vstr, n):
        vstr.store(regs[n], self.address(vstr, n+1))
        return regs[n]
    def reduce(self, vstr, n):
        vstr.load(self.address(vstr, n), regs[n])
        return regs[n]

class Call(Expr):
    def __init__(self, primary, args):
        for i, param in enumerate(primary.type.params):
            assert param == args[i].type, f'Line {primary.token.line}: Argument #{i+1} of {primary.token.lexeme} {param} != {args[i].type}'
        super().__init__(primary.type.ret, primary.token)
        self.primary, self.args = primary, args
    def reduce(self, vstr, n):
        self.generate(vstr, n)
        return regs[n]
    def generate(self, vstr, n):
        for arg in reversed(self.args):
            arg.reduce(vstr, n)
            vstr.push(regs[n])
        self.primary.call(vstr, n)
        if self.primary.type.variable and len(self.args) > len(self.primary.type.params):
            vstr.inst(Op.ADD, Reg.SP, len(self.args) - len(self.primary.type.params))
        if n > 0 and self.type.size:
            vstr.inst(Op.MOV, regs[n], Reg.A)

class Return(Expr):
    def __init__(self, token, expr):
        super().__init__(Void() if expr is None else expr.type, token)
        self.expr = expr
    def generate(self, vstr, n):
        assert vstr.defn.type.ret == self.type, f'Line {self.token.line}: {vstr.defn.type.ret} != {self.type} in {vstr.defn.token.lexeme}'
        if self.expr:
            self.expr.reduce(vstr, n)
        vstr.jump(Cond.JR, f'.L{vstr.return_label}')

class Statement(CNode):
    pass

class If(Statement):
    def __init__(self, cond, state):
        self.cond, self.true, self.false = cond, state, None
    def generate(self, vstr, n):
        vstr.if_jump_end = False
        label = vstr.next_label()
        sublabel = vstr.next_label() if self.false else label
        self.cond.compare(vstr, n, sublabel)
        self.true.generate(vstr, n)
        if self.false:
            if not (isinstance(self.true, Return) or (isinstance(self.true, Block) and self.true and isinstance(self.true[-1], Return))):
                vstr.jump(Cond.JR, f'.L{label}')
                vstr.if_jump_end = True
            vstr.append_label(f'.L{sublabel}')
            self.false.branch(vstr, n, label)
            if vstr.if_jump_end:
                vstr.append_label(f'.L{label}')
        else:
            vstr.append_label(f'.L{label}')
    def branch(self, vstr, n, root):
        sublabel = vstr.next_label()
        self.cond.compare(vstr, n, sublabel)
        self.true.generate(vstr, n)
        if self.false:
            if not (isinstance(self.true, Return) or (isinstance(self.true, Block) and self.true and isinstance(self.true[-1], Return))):
                vstr.jump(Cond.JR, f'.L{root}')
                vstr.if_jump_end = True
            vstr.append_label(f'.L{sublabel}')
            self.false.branch(vstr, n, root)

class Case(Statement):
    def __init__(self, const, statement):
        self.const, self.statement = const, statement

class Switch(Statement):
    def __init__(self, test):
        self.test, self.cases, self.default = test, [], None
    def generate(self, vstr, n):
        vstr.begin_loop()
        self.test.reduce(vstr, n)
        labels = []
        for case in self.cases:
            labels.append(vstr.next_label())
            vstr.inst(Op.CMP, regs[n], case.const.num_reduce(vstr, n+1))
            vstr.jump(Cond.JEQ, f'.L{labels[-1]}')
        if self.default:
            default = vstr.next_label()
            vstr.jump(Cond.JR, f'.L{default}')
        else:
            vstr.jump(Cond.JR, f'.L{vstr.loop.end()}')
        for i, case in enumerate(self.cases):
            vstr.append_label(f'.L{labels[i]}')
            case.statement.generate(vstr, n)
        if self.default:
            vstr.append_label(f'.L{default}')
            self.default.generate(vstr, n)
        vstr.append_label(f'.L{vstr.loop.end()}')
        vstr.end_loop()

class While(Statement):
    def __init__(self, cond, state):
        self.cond, self.state = cond, state
    def generate(self, vstr, n):
        vstr.begin_loop()
        vstr.append_label(f'.L{vstr.loop.start()}')
        self.cond.compare(vstr, n, vstr.loop.end())
        self.state.generate(vstr, n)
        vstr.jump(Cond.JR, f'.L{vstr.loop.start()}')
        vstr.append_label(f'.L{vstr.loop.end()}')
        vstr.end_loop()

class Do(Statement):
    def __init__(self, state, cond):
        self.state, self.cond = state, cond
    def generate(self, vstr, n):
        vstr.begin_loop()
        vstr.append_label(f'.L{vstr.loop.start()}')
        self.state.generate(vstr, n)
        self.cond.compare_false(vstr, n, vstr.loop.start())
        vstr.append_label(f'.L{vstr.loop.end()}')
        vstr.end_loop()

class For(While):
    def __init__(self, inits, cond, steps, state):
        super().__init__(cond, state)
        self.inits, self.steps = inits, steps
    def generate(self, vstr, n):
        for init in self.inits:
            init.generate(vstr, n)
        loop = vstr.next_label()
        vstr.begin_loop()
        vstr.append_label(f'.L{loop}')
        self.cond.compare(vstr, n, vstr.loop.end())
        self.state.generate(vstr, n)
        vstr.append_label(f'.L{vstr.loop.start()}')
        for step in self.steps:
            step.generate(vstr, n)
        vstr.jump(Cond.JR, f'.L{loop}')
        vstr.append_label(f'.L{vstr.loop.end()}')
        vstr.end_loop()

class Continue(Statement):
    def generate(self, vstr, n):
        vstr.jump(Cond.JR, f'.L{vstr.loop.start()}')

class Break(Statement):
    def generate(self, vstr, n):
        vstr.jump(Cond.JR, f'.L{vstr.loop.end()}')

class Goto(Statement):
    def __init__(self, target):
        self.target = target
    def generate(self, vstr, n):
        vstr.jump(Cond.JR, self.target.lexeme)

class Label(Statement):
    def __init__(self, target):
        self.target = target
    def generate(self, vstr, n):
        vstr.append_label(self.target.lexeme)

class Program(UserList, CNode):
    def generate(self):
        regs.clear()
        emitter = Emitter()
        for statement in self:
            statement.generate(emitter)
        return '\n'.join(emitter.data + emitter.asm)