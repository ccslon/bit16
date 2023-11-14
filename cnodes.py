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
        
class Env:
    def clear(self):
        self.labels = 0
        self.loop = Loop()
        self.if_jump_end = False
        self.strings = []
    def begin_func(self):
        pass
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
        self.asm.append(f'{name}: space {size}')
    def glob(self, name, value):
        self.asm.append(f'{name}: {value}')
    def push(self, lr, *regs):
        if lr:
            regs = (Reg.LR,) + regs
        if regs:
            self.func.insert(0, '  PUSH '+', '.join(reg.name for reg in regs))
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
        self.asm.append(f'  {value}')
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

class Type: #TODO
    def __init__(self, type):
        self.type = type
        self.size = 0 if type.lexeme == 'void' else 1
    def store(self, local, n, base):
        emit.store(r[n], r[base], local.location, local.token.lexeme)
    def address(self, local, n, base):
        emit.inst4(Op.ADD, r[n], r[base], local.location)
        return r[n]
    def reduce(self, local, n, base):
        emit.load(r[n], r[base], local.location, local.token.lexeme)
        return r[n]
    def ret(self, local, n, base):
        self.reduce(local, n, base)
    def glob(self, glob):
        if self.init:
            emit.glob(glob.token.lexeme, self.init.value)
        else:
            emit.space(glob.token.lexeme, 1)

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
        if local.location is not None:
            emit.inst4(Op.ADD, r[n], r[base], local.location)
        return r[n]
    def store(self, local, n, base):
        self.address(local, self.size, base)
        emit.storem(r[0], self.size)
    def reduce(self, local, n, base):
        self.address(local, self.size, base)
        emit.loadm(r[0], self.size)
        return r[n]
    def ret(self, local, n, base):
        self.reduce(local, 0, base)
    def glob(self, glob):
        if glob.init:
            emit.asm.append(f'{glob.token.lexeme}:')
            for expr in glob.init:
                emit.data(expr.value)
        else:
            emit.space(glob.token.lexeme, self.size)               
    
class Array(Type):
    def __init__(self, of, length):
        self.size = of.size * length.value
        self.of = of
        self.length = length.value    
    def address(self, local, n, base):
        emit.inst4(Op.ADD, r[n], r[base], local.location) 
        return r[n]
    def store(self, local, n, base):
        self.address(local, n+self.size, base)
        emit.storem(r[n], self.size)
    def reduce(self, local, n, base):
        return self.address(local, n, base)

class Expr:
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
    def num_reduce(self, n):
        if -32 <= self.value < 64:
            return self.value
        else:
            emit.imm(r[n], self.value)
            return r[n]

class Char(Expr):
    def __init__(self, token):
        self.token = token
    def reduce(self, n):
        emit.imm(r[n], self.token.lexeme)
        return r[n]

class String(Expr):
    def __init__(self, token):
        self.value = token.lexeme[1:-1]
    def reduce(self, n):
        if self.value not in env.strings:
            env.strings.append(self.value)
            emit.glob(f'.S{env.strings.index(self.value)}', f'"{self.value}\\0"')
        emit.load_glob(r[n], f'.S{env.strings.index(self.value)}')
        return r[n]

class AddrOf(Expr):
    def __init__(self, unary):
        self.unary = unary
    def reduce(self, n):
        return self.unary.address(n)

class Deref(Expr):
    def __init__(self, to):
        self.to = to
    def store(self, n):
        self.to.reduce(n+1)
        emit.store(r[n], r[n+1])
    def reduce(self, n):
        self.to.reduce(n)
        emit.load(r[n], r[n])
        return r[n]

class Unary(Expr):
    OP = {'-':Op.NEG,
          '~':Op.NOT}
    def __init__(self, sign, primary):
        self.sign, self.primary = self.OP[sign.lexeme], primary
    def reduce(self, n):
        emit.inst(self.sign, self.primary.reduce(n), Reg.A)
        return r[n]

class Post(Expr):
    OPS = {'++':Op.ADD,
           '--':Op.SUB}
    def __init__(self, op, postfix):
        self.op, self.postfix = self.OPS[op.lexeme], postfix
    def reduce(self, n):
        self.generate(n)
        return r[n]
    def generate(self, n):
        self.postfix.reduce(n)
        emit.inst4(self.op, r[n+1], r[n], 1)
        self.postfix.store(n+1)
        return r[n]

class Pre(Expr):
    OPS = {'++':Op.ADD,
           '--':Op.SUB}
    def __init__(self, op, unary):
        self.op, self.unary = self.OPS[op.lexeme], unary
    def reduce(self, n):
        self.generate(n)
        return r[n]
    def generate(self, n):
        self.unary.reduce(n)
        emit.inst(self.op, r[n], 1)
        self.unary.store(n)

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
    def reduce(self, n):        
        emit.inst(self.op, self.left.reduce(n), self.right.num_reduce(n+1))
        return r[n]

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
        # assert self.left.type() == self.right.type(), f'{self.left.type()} != {self.right.type()} in {env.func.id.name}'
        emit.inst(Op.CMP, self.left.reduce(n), self.right.num_reduce(n+1))
        emit.jump(self.inv, f'.L{label}')
    def compare_false(self, n, label):
        # assert self.left.type() == self.right.type()
        emit.inst(Op.CMP, self.left.reduce(n), self.right.num_reduce(n+1))
        emit.jump(self.op, f'.L{label}')
    def reduce(self, n):
        # assert self.left.type() == self.right.type()
        label = env.next_label()
        sublabel = env.next_label()
        emit.inst(Op.CMP, self.left.reduce(n), self.right.num_reduce(n+1))
        emit.jump(self.inv, f'.L{sublabel}')
        emit.inst(Op.MOV, Reg(n), 1)
        emit.jump(Cond.JR, f'.L{label}')
        emit.labels.append(f'.L{sublabel}')
        emit.inst(Op.MOV, Reg(n), 0)
        emit.labels.append(f'.L{label}')
        return Reg(n)

class Logic(Binary):
    OP = {'&&':Op.AND,
          '||':Op.OR}
    def __init__(self, op, left, right):
        self.op, self.left, self.right = self.OP[op.lexeme], left, right
    def compare(self, n, label):
        # assert self.left.type() == self.right.type()
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
        self.cond, self.true, self.false = cond, true, false
    def reduce(self, n):
        env.if_jump_end = False
        label = env.next_label()
        sublabel = env.next_label() if self.false else label
        self.cond.compare(n, sublabel)
        self.true.reduce(n)
        emit.jump(Cond.JR, f'.L{label}')
        emit.labels.append(f'.L{sublabel}')
        self.false.branch(n, label)
        emit.labels.append(f'.L{label}')
    def branch(self, n, root):
        sublabel = env.next_label()
        self.cond.compare(n, sublabel)
        self.true.reduce(n)
        emit.jump(Cond.JR, f'.L{root}')
        emit.labels.append(f'.L{sublabel}')
        self.false.branch(n, root)

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

class Glob(Local):
    def __init__(self, type, token):
        super().__init__(type, token)
        self.location = None
        self.init = None
    def store(self, n):
        self.address(n)
        return self.type.store(self, n, n+1)
    def reduce(self, n):
        self.address(n)
        return self.type.reduce(self, n, n)
    def address(self, n):
        emit.load_glob(r[n], self.token.lexeme)
        return r[n]
    def ret(self, n):
        self.address(n)
        self.type.ret(self, n, n)
    def generate(self): #TODO
        self.type.glob(self)

class List(Expr, UserList):
    def reduce(self, n):
        for i, expr in enumerate(self):
            expr.reduce(n+i)
        return r[n]

class Params(Expr, UserList):
    def generate(self):
        for i, param in enumerate(self):
            emit.store(r[i], Reg.SP, i, param.token.lexeme)
    
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
        if self.type.size: 
            emit.func.append(f'.L{env.return_label}:')
        if type(self.type) is not Struct and self.max_args is not None and self.max_args > 0 and self.type.size:
            emit.inst(Op.MOV, Reg.A, r[self.max_args])
        if self.space:
            emit.inst(Op.ADD, Reg.SP, self.space)
        push = list(map(Reg, range(max(len(self.params), self.type.size), r.max+1))) 
        emit.push(self.max_args is not None, *push)
        emit.pop(self.max_args is not None, *push)
        emit.func.insert(0, f'{self.id.lexeme}:')
        if self.max_args is None:
            emit.ret()
        emit.end_func()

class Main(Expr):
    def __init__(self, block, space):
        self.block, self.space = block, space
    def generate(self):
        env.begin_func()
        emit.begin_func()
        if self.space:
            emit.inst(Op.SUB, Reg.SP, self.space)
        self.block.generate(0)
        if self.space:
            emit.inst(Op.ADD, Reg.SP, self.space)
        emit.halt()
        emit.end_func()

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
        emit.inst(Op.ADD, self.postfix.reduce(n), self.attr.location)
        return r[n] 
    def store(self, n):
        self.postfix.reduce(n+1)
        return self.attr.store(n)
    def reduce(self, n):
        self.postfix.reduce(n)
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
        emit.store(r[n], self.address(n+1))
        return r[n]
    def reduce(self, n):
        emit.load(self.address(n), r[n])
        return r[n]

class If(Expr):
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

class Case(Expr):
    def __init__(self, const, statement):
        self.const, self.statement = const, statement

class Switch(Expr):
    def __init__(self, test):
        self.test, self.cases, self.default = test, [], None
    def generate(self, n):
        env.begin_loop()
        self.test.reduce(n)
        labels = []
        for case in self.cases:
            labels.append(env.next_label())
            emit.inst(Op.CMP, r[n], case.const.num_reduce(n))
            emit.jump(Cond.JEQ, f'.L{labels[-1]}')
        emit.jump(Cond.JR, f'.L{env.loop.end()}')
        for i, case in enumerate(self.cases):
            emit.labels.append(f'.L{labels[i]}')
            case.statement.generate(n)
        emit.labels.append(f'.L{env.loop.end()}')
        if self.default:
            self.default.generate(n)            
        env.end_loop()

class While(Expr):
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

class Do(Expr):
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

class Continue(Expr):
    def generate(self, n):
        emit.jump(Cond.JR, f'.L{env.loop.start()}')
        
class Break(Expr):
    def generate(self, n):
        emit.jump(Cond.JR, f'.L{env.loop.end()}')

class Goto(Expr):
    def __init__(self, target):
        self.target = target
    def generate(self, n):
        emit.jump(Cond.JR, self.target.lexeme)
        
class Label(Expr):
    def __init__(self, target):
        self.target = target
    def generate(self, n):
        emit.labels.append(self.target.lexeme)

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
        if n > 0 and type(self.primary.type) is not Struct:
            emit.inst(Op.MOV, r[n], Reg.A)
        return r[n]

class Return(Expr):
    def __init__(self):
        self.expr = None
    def generate(self, n):
        # assert self.type() == env.func.type_spec, f'{self.expr.type()} != {env.func.type_spec} in {env.func.id.name}'       
        if self.expr:
            self.expr.ret(n)
        emit.jump(Cond.JR, f'.L{env.return_label}')

class Program(Expr, UserList):
    def generate(self):
        r.clear()
        env.clear()
        emit.clear()
        for statement in self:
            statement.generate()
        return '\n'.join(emit.asm)