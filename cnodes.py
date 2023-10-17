# -*- coding: utf-8 -*-
"""
Created on Mon Jul  3 19:48:36 2023

@author: Colin
"""
from collections import UserList
from bit16 import Reg, Op, Cond
#TODO Add div and mod

class Loop(UserList):
    def start(self):
        return self[-1][0]
    def end(self):
        return self[-1][1]

class SetList(UserList):
    def add(self, item):
        if item not in self:
            self.append(item)    

class Frame:
    def __init__(self, old=None):
        if old is None:
            self.locals = {}
            self.size = 0
        else:
            self.locals = old.locals.copy()
            self.size = old.size
    def index(self, name):
        return self.locals[name]
    def append(self, name, size):
        self.locals[name] = self.size
        self.size += size

class Scope():
    def __init__(self, old):
        if old is None:
            self.frame = Frame()
            self.locals = {}
        else:
            self.frame = Frame(old.frame)
            self.locals = old.locals.copy()
    def decl(self, type_spec, name):
        self.locals[name] = type_spec
        self.frame.append(name, type_spec.size())
    def resolve(self, name):
        return self.frame.index(name)

class Env:
    def __init__(self):
        self.labels = 0
        self.loop = Loop()
        self.globals = SetList()
        self.strings = []
        self.functions = []
        self.if_jump_end = False
        self.scope = None
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
    def address(self, name, n):
        if name in self.scope.locals:
            self.scope.locals
    def declare(self, decl):
        self.scope.decl(decl.type_spec, decl.id.name)
    def resolve(self, id_):
        return self.scope.resolve(id_.name)
    def member(self, id_, member): #TODO
        if id_.name in self.scope.locals:
            return self.scope.locals[id_.name].id_.name

class Traveler:
    def __init__(self):
        self.env = Env()
        self.labels = []
        self.asm = []
    def add(self, asm):
        for label in self.labels:
            self.asm.append(f'{label}:')
        self.asm.append(f'  {asm}')
        self.labels.clear()
    def glob(self, name, value):
        self.asm.append(f'{name}: {value}')
    def push(self, lr, *regs):
        if lr:
            regs = (Reg.LR,) + regs
        if regs:
            self.add('PUSH '+', '.join(reg.name for reg in regs))
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
    def load(self, rd, rb, offset5=None, name=None):
        self.add(f'LD {rd.name}, [{rb.name}'+(f', {offset5}' if offset5 is not None else '')+']'+(f' ; {name}' if name else ''))
    def store(self, rd, rb, offset5=None, name=None):
        self.add(f'LD [{rb.name}'+(f', {offset5}' if offset5 is not None else '')+f'], {rd.name}'+(f' ; {name}' if name else ''))
    def imm(self, rd, value):
        self.add(f'LD {rd.name}, {value}')
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

class Expr:
    def load(self, trav, n):
        return self.compile(trav, n)
    def branch(self, trav, n, _):
        self.compile(trav, n)
    def compare(self, trav, n, label):
        trav.inst(Op.CMP, self.compile(trav, n), 0)
        trav.jump(Cond.JR, f'.L{label}')
    def analyze(self, trav, n):
        pass
    def analyze_right(self, trav, n):
        self.analyze(trav, n)
    def analyze_store(self, trav, n):
        self.analyze(trav, n)
    def __str__(self):
        return f'{self.__class__.__name__}()'
    
class Const(Expr):
    def __init__(self, value):
        if value == 'true':
            self.value = 1
        elif value in ['false','null']:
            self.value = 0
        elif value.startswith('0x'):
            self.value = int(value, base=16)
        elif value.startswith('0b'):
            self.value = int(value, base=2)
        else:
            self.value = int(value)
    def analyze(self, trav, n):
        trav.env.regs = max(trav.env.regs, n)
    def analyze_right(self, trav, n):
        if not (-32 <= self.value < 64):
            self.analyze(trav, n)
    def load(self, trav, n):
        if -32 <= self.value < 64:
            trav.inst(Op.MOV, Reg(n), self.value)
        else:
            trav.imm(Reg(n), self.value)
        return Reg(n)
    def compile(self, trav, n):
        # if -32 <= self.value < 64:
        #     return self.value
        # else:
        #     trav.imm(Reg(n), self.value)
        # return Reg(n)
        return self.value
    def __str__(self):
        return f"{self.__class__.__name__}({self.value})"

class Char(Expr):
    def __init__(self, value):
        self.value = value
    def analyze(self, trav, n):
        trav.env.regs = max(trav.env.regs, n)
    def compile(self, trav, n):
        trav.imm(Reg(n), self.value)
        return Reg(n)
    
class String(Expr):
    def __init__(self, value):
        self.value = value[1:-1]
    def analyze(self, trav, n):
        trav.env.regs = max(trav.env.regs, n)
        if self.value not in trav.env.strings:
            trav.env.strings.append(self.value)
            trav.glob(f'.S{trav.env.strings.index(self.value)}', f'"{self.value}\0"')
    def load(self, trav, n):
        trav.load_glob(Reg(n), f'.S{trav.env.strings.index(self.value)}')
    def compile(self, trav, n):
        return f'"{self.value}\0"'

class Id(Expr):
    def __init__(self, name):
        self.name = name
    def analyze(self, trav, n):
        trav.env.regs = max(trav.env.regs, n)
    def address(self, trav, n):
        if self.name in trav.env.scope.locals:
            trav.env.scope.locals[self.name].address(self, trav, n)
            # trav.inst4(Op.ADD, Reg(n), Reg.SP, trav.env.resolve(self))
        elif self.name in trav.env.globals:
            trav.load_glob(Reg(n), self.name)
        return Reg(n)
    def store(self, trav, n):
        if self.name in trav.env.scope.locals:
            trav.env.scope.locals[self.name].store(self, trav, n)
        elif self.name in trav.env.globals:
            trav.load_glob(Reg(n+1), self.name)
            trav.store(Reg(n), Reg(n+1))
    def compile(self, trav, n):
        if self.name in trav.env.scope.locals:
            trav.env.scope.locals[self.name].compile(self, trav, n)
        elif self.name in trav.env.globals:
            trav.load_glob(Reg(n), self.name)
            trav.load(Reg(n), Reg(n))
        return Reg(n)
    def __str__(self):
        return f"{self.__class__.__name__}('{self.name}')"    

class Address(Expr):
    def __init__(self, unary):
        self.unary = unary
    def analyze(self, trav, n):
        self.unary.analyze(trav, n)
    def analyze_store(self, trav, n):
        self.analyze(trav, n+1)
    def compile(self, trav, n):
        self.unary.address(trav, n)
        return Reg(n)
    def __str__(self):
        return f'{self.__class__.__name__}({self.unary})'

class Pointer(Expr):
    def __init__(self, to):
        self.to = to
    def analyze(self, trav, n):
        self.to.analyze(trav, n)
    def store(self, trav, n):
        self.to.compile(trav, n+1)
        trav.store(Reg(n), Reg(n+1))
    def compile(self, trav, n):
        self.to.compile(trav, n)
        trav.load(Reg(n), Reg(n))
        return Reg(n)
    def __str__(self):
        return f'{self.__class__.__name__}({self.to})'

class Unary(Expr):
    OPS = {'-':Op.NEG,
           '!':Op.NOT,
           '~':Op.NOT}
    def __init__(self, sign, primary):
        self.sign, self.primary = self.OPS[sign], primary
    def analyze(self, trav, n):
        self.primary.analyze(trav, n)
    def compile(self, trav, n):
        trav.inst(self.sign, self.primary.compile(trav, n), Reg.A)
        return Reg(n)
    def __str__(self):
        return f'{self.sign[0].upper() + self.sign[1:]}({self.primary})'

class Cast(Expr):
    def __init__(self, target, cast):
        self.target, self.cast = target, cast

class Conditional(Expr):
    def __init__(self, logic_or, expr, cond):
        self.logic_or, self.expr, self.cond = logic_or, expr, cond

class Type(Expr): #TODO
    def __init__(self, type_):
        self.type = type_
        self.size = lambda: 1
    def address(self, id_, trav, n):
        trav.inst4(Op.ADD, Reg(n), Reg.SP, trav.env.resolve(id_))
    def store(self, id_, trav, n):
        trav.store(Reg(n), Reg.SP, trav.env.resolve(id_), id_.name)
    def compile(self, id_, trav, n):
        trav.load(Reg(n), Reg.SP, trav.env.resolve(id_), id_.name)
            
class PointerType(Type):
    pass
        
class Array(Type):
    def __init__(self, of, size):
        self.of = of
        self.size = lambda: self.of.size() * size.value
    def address(self, id_, trav, n):
        trav.inst4(Op.ADD, Reg(n), Reg.SP, trav.env.resolve(id_))
    def compile(self, id_, trav, n):
        self.address(id_, trav, n)

class StructType(Type):
    def __init__(self, name, size):
        self.name, self.size = name, size
    def address(self, id_, trav, n):
        trav.inst4(Op.ADD, Reg(n), Reg.SP, trav.env.resolve(id_))
    def compile(self, id_, trav, n):
        self.address(id_, trav, n)
        
class Decl(Expr):
    def __init__(self, type_spec, id_):
        self.type_spec, self.id = type_spec, id_
    def analyze(self, trav, n):
        self.id.analyze(trav, n)
        trav.env.space += self.type_spec.size()
    def store(self, trav, n):
        self.compile(trav, n)
        self.id.store(trav, n)
    def compile(self, trav, n):
        trav.env.declare(self) #self.local.compile(trav, n)

class Binary(Expr):    
    OPS = {'+' :Op.ADD,
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
        self.op, self.left, self.right = self.OPS[op], left, right
    def analyze(self, trav, n):
        self.left.analyze(trav, n)
        self.right.analyze_right(trav, n+1)
    def compile(self, trav, n):
        trav.inst(self.op, self.left.load(trav, n), self.right.compile(trav, n+1))
        return Reg(n)
    def __str__(self):
        return f'{self.op[0].upper() + self.op[1:]}({self.left},{self.right})'

class Compare(Binary):
    OPS = {'==':'eq',
           '!=':'ne',
           '>': 'gt',
           '<': 'lt',
           '>=':'ge',
           '<=':'le'}
    INV = {'eq':Cond.JNE,
           'ne':Cond.JEQ,
           'gt':Cond.JLE,
           'lt':Cond.JGE,
           'ge':Cond.JLT,
           'le':Cond.JGT}
    def compare(self, trav, n, label):
        trav.inst(Op.CMP, self.left.load(trav, n), self.right.compile(trav, n+1))
        trav.jump(self.INV[self.op], f'.L{label}')
    def compile(self, trav, n):
        label = trav.env.next_label()
        sublabel = trav.env.next_label()
        trav.inst(Op.CMP, self.left.load(trav, n), self.right.compile(trav, n+1))
        trav.jump(self.INV[self.op], f'.L{sublabel}')
        trav.inst(Op.MOV, Reg(n), 1)
        trav.jump(Cond.JR, f'.L{label}')
        trav.labels.append(f'.L{sublabel}')
        trav.inst(Op.MOV, Reg(n), 0)
        trav.labels.append(f'.L{label}')        

class Logic(Binary):
    OPS = {'and':Op.AND,
           'or':Op.OR}
    def __init__(self, op, left, right):
        self.op, self.left, self.right = self.OPS[op], left, right
    def compare(self, trav, n, label):
        if self.op == Op.AND:
            trav.inst(Op.CMP, self.left.compile(trav, n), 0)
            trav.jump(Cond.JEQ, f'.L{label}')
            trav.inst(Op.CMP, self.right.compile(trav, n), 0)
            trav.jump(Cond.JEQ, f'.L{label}')
        elif self.op == Op.OR:
            sublabel = trav.env.next_label()
            trav.inst(Op.CMP, self.left.compile(trav, n), 0)
            trav.jump(Cond.JNE, f'.L{sublabel}')
            trav.inst(Op.CMP, self.right.compile(trav, n), 0)
            trav.jump(Cond.JEQ, f'.L{label}')
            trav.labels.append(f'.L{sublabel}')
    def compile(self, trav, n):
        trav.inst(self.op, self.left.load(trav, n), self.right.compile(trav, n+1))

class Assign(Expr):
    def __init__(self, left, right):
        self.left, self.right = left, right
    def analyze(self, trav, n):
        self.right.analyze(trav, n)
        self.left.analyze_store(trav, n)
    def compile(self, trav, n):
        self.right.load(trav, n)
        self.left.store(trav, n)
        return Reg(n)
    def __str__(self):
        return f'{self.__class__.__name__}({self.left},{self.right})'

class Args(Expr, UserList):
    def analyze(self, trav, n):        
        for i, arg in enumerate(self, n):
            arg.analyze(trav, i)
    def compile(self, trav, n):
        for i, arg in enumerate(self, n):
            arg.load(trav, i)
        if n > 0:
            for i, arg in enumerate(self):
                trav.inst(Op.MOV, Reg(i), Reg(n+i))
    def __str__(self):
        return f'{self.__class__.__name__}({",".join(map(str,self))})'  

class Call(Expr):
    def __init__(self, id, args):
        self.id, self.args = id, args
    def analyze(self, trav, n):
        trav.env.calls = True
        self.args.analyze(trav, n)
        trav.env.regs = max(trav.env.regs, len(self.args), n) # len(args) because args are copied e.g. A, B <- Reg(regs), Reg(regs+1). n because if no args
        trav.env.args = max(trav.env.args, len(self.args))
    def compile(self, trav, n):
        self.args.compile(trav, n)
        trav.call(self.id.name)
        if n > 0:
            trav.inst(Op.MOV, Reg(n), Reg.A)
        return Reg(n)
    def __str__(self):
        return f'{self.__class__.__name__}({self.id},{self.args})'
    
class If(Expr):
    def __init__(self, cond, state):
        self.cond, self.true, self.false = cond, state, None
    def analyze(self, trav, n):
        self.cond.analyze(trav, 1)
        self.true.analyze(trav, 1)
        if self.false:
            self.false.analyze(trav, 1)
    def compile(self, trav, n):
        trav.env.if_jump_end = False
        label = trav.env.next_label()
        sublabel = trav.env.next_label() if self.false else label
        self.cond.compare(trav, n, sublabel)
        self.true.compile(trav, n)
        if self.false:
            if not (isinstance(self.true, Return) or (isinstance(self.true, Block) and self.true and isinstance(self.true[-1], Return))):
                trav.jump(Cond.JR, f'.L{label}')
                trav.env.if_jump_end = True
            trav.labels.append(f'.L{sublabel}')
            self.false.branch(trav, n, label)
        if trav.env.if_jump_end:
            trav.labels.append(f'.L{label}')
    def branch(self, trav, n, root):
        sublabel = trav.env.next_label()
        self.cond.compare(trav, n, sublabel)
        self.true.compile(trav, n)
        if self.false:
            if not (isinstance(self.true, Return) or (isinstance(self.true, Block) and self.true and isinstance(self.true[-1], Return))):
                trav.jump(Cond.JR, f'.L{root}')
                trav.env.if_jump_end = True
            trav.labels.append(f'.L{sublabel}')
            self.false.branch(trav, n, root)     
    def __str__(self):
        return f'{self.__class__.__name__}({self.cond},{self.true},{self.false})'

class While(Expr):
    def __init__(self, cond, state):
        self.cond, self.state = cond, state
    def analyze(self, trav, n):
        self.cond.analyze(trav, 1)
        self.state.analyze(trav, 1)
    def compile(self, trav, n):
        trav.env.begin_loop()
        trav.labels.append(f'.L{trav.env.loop.start()}')
        self.cond.compare(trav, n, trav.env.loop.end())
        self.state.compile(trav, n)
        trav.jump(Cond.JR, f'.L{trav.env.loop.start()}')
        trav.labels.append(f'.L{trav.env.loop.end()}')
        trav.env.end_loop()
    def __str__(self):
        return f'{self.__class__.__name__}({self.cond},{self.state})'
        
class For(While):
    def __init__(self, init, cond, step, state):
        super().__init__(cond, state)
        self.init, self.step = init, step
    def analyze(self, trav, n):
        self.init.analyze(trav, 1)
        super().analyze(trav, 1)
        self.step.analyze(trav, 1)
    def compile(self, trav, n):
        self.init.compile(trav, n)
        trav.env.begin_loop()
        trav.labels.append(f'.L{trav.env.loop.start()}')
        self.cond.compare(trav, n, trav.env.loop.end())
        self.state.compile(trav, n)
        self.step.compile(trav, n)
        trav.jump(Cond.JR, f'.L{trav.env.loop.start()}')
        trav.labels.append(f'.L{trav.env.loop.end()}')
        trav.env.end_loop()
    def __str__(self):
        return f'{self.__class__.__name__}({self.init},{self.cond},{self.step},{self.state})'

class Continue(Expr):
    def compile(self, trav, n):
        trav.jump(Cond.JR, f'.L{trav.env.loop.start()}')
        
class Break(Expr):
    def compile(self, trav, n):
        trav.jump(Cond.JR, f'.L{trav.env.loop.end()}')

class Return(Expr):
    def __init__(self):
        self.expr = None
    def analyze(self, trav, n):
        trav.env.returns = True
        if self.expr:
            self.expr.analyze(trav, 1)
    def compile(self, trav, n):
        if self.expr:
            self.expr.load(trav, n)
        trav.jump(Cond.JR, f'.L{trav.env.func}')
    def __str__(self):
        return f"{self.__class__.__name__}({self.expr})"
        
class Script(Expr):
    def __init__(self, id, sub):
        self.id, self.sub = id, sub
    def analyze(self, trav, n):
        self.id.analyze(trav, n)
        self.sub.analyze(trav, n+1)
    def analyze_store(self, trav, n):
        self.analyze(trav, n+1)
    def address(self, trav, n):
        self.id.compile(trav, n)
        self.sub.compile(trav, n+1)
        trav.inst(Op.ADD, Reg(n), Reg(n+1))
    def store(self, trav, n):
        self.address(trav, n+1)
        trav.store(Reg(n), Reg(n+1))
    def compile(self, trav, n):
        self.address(trav, n)
        trav.load(Reg(n), Reg(n))
        return Reg(n)

class Arrow(Expr): #TODO
    def __init__(self, id_, attr):
        self.id, self.attr = id_, attr

class Attr(Expr): #TODO
    def __init__(self, id_, attr):
        self.id, self.attr = id_, attr
    def analyze(self, trav, n):
        self.id.analyze(trav, n)
    def analyze_store(self, trav, n):
        self.analyze(trav, n+1)
    def address(self, trav, n):
        self.id.compile(trav, n)
        trav.inst(Op.ADD, Reg(n), trav.env.structs[self.attr])
    def store(self, trav, n):
        self.address(trav, n+1)
        trav.store(Reg(n), Reg(n+1), 0)
    def compile(self, trav, n):
        self.address(trav, n)
        trav.load(Reg(n), Reg(n), 0)

class Global(Assign):
    def declare(self, trav):
        trav.env.globals.add(self.left.name)
    def compile(self, trav):
        trav.glob(self.left.name, self.right.compile(trav, 0))

class Fields(Expr, UserList):    
    def declare(self, trav):
        return {field.id.name:i for i, field in enumerate(self)} 

class Struct(Expr):
    def __init__(self, id_, fields=Fields()):
        self.id, self.fields = id_, fields
    def declare(self, trav):
        trav.structs[self.id.name] = self.fields.declare(trav)
    def compile(self, trav):
        pass

class Params(Expr, UserList):
    def analyze(self, trav):
        for param in self:
            param.analyze(trav, 0)
    def compile(self, trav):
        for i, param in enumerate(self):
            param.compile(trav, 0)
            trav.store(Reg(i), Reg.SP, trav.env.resolve(param.id))

class Block(Expr, UserList):
    def analyze(self, trav, n):
        for statement in self:
            statement.analyze(trav, n)
    def compile(self, trav, n):
        trav.env.begin_scope()
        for statement in self:
            statement.compile(trav, trav.env.args)
        trav.env.end_scope()
    def __str__(self):
        nl = ",\n"
        return f'{self.__class__.__name__}(\n{nl.join(map(str,self))}\n)'

class Func(Expr):
    def __init__(self, type_spec, id_, params, block):
        self.type_spec, self.id, self.params, self.block = type_spec, id_, params, block
    def declare(self, trav):
        trav.env.functions.append(self)
    def compile(self, trav):
        trav.env.begin_func()
        trav.env.begin_scope()
        self.params.analyze(trav)
        self.block.analyze(trav, 1)
        if trav.env.returns:
            trav.env.func = trav.env.next_label()
        trav.labels.append(self.id.name)
        #print(trav.env.args, trav.env.regs)
        push = list(map(Reg, range(max(len(self.params), trav.env.returns), trav.env.args + trav.env.regs)))
        trav.push(trav.env.calls, *push)
        if trav.env.space:
            trav.inst(Op.SUB, Reg.SP, trav.env.space)
        self.params.compile(trav)
        self.block.compile(trav, trav.env.args)
        if trav.env.returns:
            trav.labels.append(f'.L{trav.env.func}')
            if trav.env.args > 0:
                trav.inst(Op.MOV, Reg.A, Reg(trav.env.args))
        if trav.env.space:
            trav.inst(Op.ADD, Reg.SP, trav.env.space)
        trav.pop(trav.env.calls, *push)
        if not trav.env.calls:
            trav.ret()
        trav.env.end_scope()
    def __str__(self):
        return f'{self.__class__.__name__}({self.id},{self.params},{self.block})'

class Main(Expr):
    def __init__(self, block):
        self.block = block
    def declare(self, trav):
        pass
    def compile(self, trav):
        trav.env.begin_func()
        trav.env.begin_scope()
        self.block.analyze(trav, 1)
        if trav.env.scope.locals:
            trav.inst(Op.SUB, Reg.SP, trav.env.scope.frame.size)
        self.block.compile(trav, 0)
        if trav.env.scope.locals:
            trav.inst(Op.ADD, Reg.SP, trav.env.scope.frame.size)
        trav.halt()
        trav.env.end_scope()

class Program(Expr, UserList):
    def compile(self):
        trav = Traveler()
        for decl in self:
            decl.declare(trav)
        for decl in self:
            decl.compile(trav)
        return '\n'.join(trav.asm)
    def __str__(self):
        nl = ",\n"
        return f'{self.__class__.__name__}(\n{nl.join(map(str,self))}\n)'