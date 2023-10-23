# -*- coding: utf-8 -*-
"""
Created on Mon Jul  3 19:48:36 2023

@author: Colin
"""
from collections import UserList, UserDict
from bit16 import Reg, Op, Cond, ESCAPE
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

class Frame(UserDict):
    def __init__(self):          
        self.size = 0
        self.indices = {}
        super().__init__()
    def __setitem__(self, name, type_spec):
        self.indices[name] = self.size
        self.size += type_spec.size
        super().__setitem__(name, type_spec)
    def index(self, name):
        return self.indices[name]
    def copy(self):
        return self.size, self.indices.copy(), self.data.copy()

class Scope(Frame):
    def __init__(self, old=None):
        if old is None:            
            super().__init__()
        else:            
            self.size = old.size
            self.indices = old.indices.copy()  
            self.data = old.data.copy()

class Env:
    def clear(self):
        self.labels = 0
        self.loop = Loop()
        self.globals = SetList()
        self.strings = []
        self.functions = []
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
    def inst4(self, op, rd, rs, Num4):
        self.add(f'{op.name} {rd.name}, {rs.name}, {Num4}')
    def jump(self, cond, target):
        self.add(f'{cond.name} {target}')
    def halt(self):
        self.add('HALT')

emit = Emitter()

class Expr:
    def load(self, n):
        return self.compile(n)
    def branch(self, n, _):
        self.compile(n)
    def compare(self, n, label):
        emit.inst(Op.CMP, self.compile(n), 0)
        emit.jump(Cond.JEQ, f'.L{label}')
    def compare_false(self, n, label):
        emit.inst(Op.CMP, self.compile(n), 0)
        emit.jump(Cond.JNE, f'.L{label}')
    def analyze(self, n):
        pass
    def analyze_right(self, n):
        self.analyze(n)
    def analyze_store(self, n):
        self.analyze(n)
    
class Num(Expr):
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
    def analyze(self, n):
        env.regs = max(env.regs, n)
    def analyze_right(self, n):
        if not (-32 <= self.value < 64):
            self.analyze(n)
    def load(self, n):
        if -32 <= self.value < 64:
            emit.inst(Op.MOV, Reg(n), self.value)
        else:
            emit.imm(Reg(n), self.value)
        return Reg(n)
    def compile(self, n):
        return self.value

class Char(Expr):
    def __init__(self, value):
        self.value = value
    def analyze(self, n):
        env.regs = max(env.regs, n)
    def compile(self, n):
        emit.imm(Reg(n), self.value)
        return Reg(n)
    
class String(Expr):
    def __init__(self, value):
        self.value = value[1:-1]
    def analyze(self, n):
        env.regs = max(env.regs, n)
        if self.value not in env.strings:
            env.strings.append(self.value)
            emit.glob(f'.S{env.strings.index(self.value)}', f'"{self.value}\0"')
    def load(self, n):
        emit.load_glob(Reg(n), f'.S{env.strings.index(self.value)}')
    def compile(self, n):
        return f'"{self.value}\0"'

class Id(Expr):
    def __init__(self, name):
        self.name = name
    def analyze(self, n):
        env.regs = max(env.regs, n)
    def address(self, n):        
        if self.name in env.scope:
            env.scope[self.name].address(n, self.name)
        elif self.name in env.globals:
            emit.load_glob(Reg(n), self.name)
        return Reg(n)
    def get_type(self):
        return env.scope[self.name]
    def init_store(self, n):
        if self.name in env.scope:
            env.scope[self.name].init_store(n, self.name)
        elif self.name in env.globals:
            emit.load_glob(Reg(n+1), self.name)
            emit.store(Reg(n), Reg(n+1))
    def store(self, n):
        if self.name in env.scope:
            env.scope[self.name].store(n, self.name)
        elif self.name in env.globals:
            emit.load_glob(Reg(n+1), self.name)
            emit.store(Reg(n), Reg(n+1))
    def compile(self, n):
        if self.name in env.scope:
            env.scope[self.name].compile(n, self.name)
        elif self.name in env.globals:
            emit.load_glob(Reg(n), self.name)
            emit.load(Reg(n), Reg(n))
        return Reg(n)   

class Address(Expr):
    def __init__(self, unary):
        self.unary = unary
    def analyze(self, n):
        self.unary.analyze(n)
    def analyze_store(self, n):
        self.analyze(n+1)
    def compile(self, n):
        self.unary.address(n)
        return Reg(n)

class Pointer(Expr):
    def __init__(self, to):
        self.to = to
    def analyze(self, n):
        self.to.analyze(n)
    def store(self, n):
        self.to.compile(n+1)
        emit.store(Reg(n), Reg(n+1))
    def compile(self, n):
        self.to.compile(n)
        emit.load(Reg(n), Reg(n))
        return Reg(n)

class Unary(Expr):
    OP = {'-':Op.NEG,
           '~':Op.NOT}
    def __init__(self, sign, primary):
        self.sign, self.primary = self.OP[sign], primary
    def analyze(self, n):
        self.primary.analyze(n)
    def compile(self, n):
        emit.inst(self.sign, self.primary.compile(n), Reg.A)
        return Reg(n)

class Cast(Expr):
    def __init__(self, target, cast):
        self.target, self.cast = target, cast

class Conditional(Expr): #TODO
    def __init__(self, logic_or, expr, cond):
        self.logic_or, self.expr, self.cond = logic_or, expr, cond

class Type(Expr):
    def __init__(self, type_):
        self.type = type_
    def analyze(self):
        self.size = 1
    def address(self, n, name):
        emit.inst4(Op.ADD, Reg(n), Reg.SP, env.scope.index(name))
    def init_store(self, n, name):
        self.store(n, name)
    def store(self, n, name):
        emit.store(Reg(n), Reg.SP, env.scope.index(name), name)
    def compile(self, n, name):
        emit.load(Reg(n), Reg.SP, env.scope.index(name), name)
        
class Const(Expr):
    def __init__(self, type_):
        self.type = type_
    def analyze(self):
        self.type.analyze()
        self.size = self.type.size
    def address(self, n, name):
        self.type.address(n, name)
    def init_store(self, n, name):
        self.type.store(n, name)
    def store(self, n, name):
        self.type.const_store(n, name)
    def compile(self, n, name):
        self.type.compile(n, name)
        
class PointerType(Type):
    def __init__(self, to):
        self.to = to
        self.size = 1
    def analyze(self):
        self.to.analyze()
    def const_store(self, n, name):
        self.to.store(n, name)
        
class Array(Type):
    def __init__(self, of, length):
        self.of = of
        self.length = length.value
    def analyze(self):
        self.of.analyze()
        self.size = self.length * self.of.size
    def address(self, n, name):
        emit.inst4(Op.ADD, Reg(n), Reg.SP, env.scope.index(name))
    def compile(self, n, name):
        self.address(n, name)

class StructType(Type, Frame):
    def __init__(self, name):
        self.name = name
    def analyze(self):
        self.size, self.indices, self.data = env.structs[self.name].copy()
    def address(self, n, name):
        emit.inst4(Op.ADD, Reg(n), Reg.SP, env.scope.index(name))
    def compile(self, n, name):
        self.address(n, name)


class Fields(Expr, UserList):
    pass

class Struct(Expr, Frame):
    def __init__(self, name, fields=Fields()):
        self.name, self.fields = name, fields
        self.size = 0
        self.indices = {}
        self.data = {}        
    def declare(self):
        for field in self.fields:
            field.type_spec.analyze()
            field.declare(self)
        env.structs[self.name] = self
    def compile(self):
        pass

class Decl(Expr):
    def __init__(self, type_spec, id_):
        self.type_spec, self.id = type_spec, id_
    def declare(self, frame):
        frame[self.id.name] = self.type_spec
    def analyze_store(self, n):
        self.analyze(n)
        self.id.analyze(n)
    def analyze(self, n):
        self.type_spec.analyze()
        env.space += self.type_spec.size
    def store(self, n):        
        self.compile(n)
        self.id.init_store(n)
    def compile(self, n):
        self.declare(env.scope)

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
        self.op, self.left, self.right = self.OP[op], left, right
    def analyze(self, n):
        self.left.analyze(n)
        self.right.analyze_right(n+1)
    def compile(self, n):
        emit.inst(self.op, self.left.load(n), self.right.compile(n+1))
        return Reg(n)

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
        self.inv = self.INV[op]
    def compare(self, n, label):
        emit.inst(Op.CMP, self.left.load(n), self.right.compile(n+1))
        emit.jump(self.inv, f'.L{label}')
    def compare_false(self, n, label):
        emit.inst(Op.CMP, self.left.load(n), self.right.compile(n+1))
        emit.jump(self.op, f'.L{label}')
    def compile(self, n):
        label = env.next_label()
        sublabel = env.next_label()
        emit.inst(Op.CMP, self.left.load(n), self.right.compile(n+1))
        emit.jump(self.inv, f'.L{sublabel}')
        emit.inst(Op.MOV, Reg(n), 1)
        emit.jump(Cond.JR, f'.L{label}')
        emit.labels.append(f'.L{sublabel}')
        emit.inst(Op.MOV, Reg(n), 0)
        emit.labels.append(f'.L{label}')        

class Logic(Binary):
    OP = {'&&':Op.AND,
          '||':Op.OR}
    def __init__(self, op, left, right):
        self.op, self.left, self.right = self.OP[op], left, right
    def compare(self, n, label):
        if self.op == Op.AND:
            emit.inst(Op.CMP, self.left.compile(n), 0)
            emit.jump(Cond.JEQ, f'.L{label}')
            emit.inst(Op.CMP, self.right.compile(n), 0)
            emit.jump(Cond.JEQ, f'.L{label}')
        elif self.op == Op.OR:
            sublabel = env.next_label()
            emit.inst(Op.CMP, self.left.compile(n), 0)
            emit.jump(Cond.JNE, f'.L{sublabel}')
            emit.inst(Op.CMP, self.right.compile(n), 0)
            emit.jump(Cond.JEQ, f'.L{label}')
            emit.labels.append(f'.L{sublabel}')
    def compile(self, n):
        emit.inst(self.op, self.left.load(n), self.right.compile(n+1))

class Assign(Expr):
    def __init__(self, left, right):
        self.left, self.right = left, right
    def analyze(self, n):
        self.right.analyze(n)
        self.left.analyze_store(n)
    def compile(self, n):
        self.right.load(n)
        self.left.store(n)
        return Reg(n)

class Args(Expr, UserList):
    def analyze(self, n):        
        for i, arg in enumerate(self, n):
            arg.analyze(i)
    def compile(self, n):
        for i, arg in enumerate(self, n):
            arg.load(i)
        if n > 0:
            for i, arg in enumerate(self):
                emit.inst(Op.MOV, Reg(i), Reg(n+i)) 

class Call(Expr):
    def __init__(self, id, args):
        self.id, self.args = id, args
    def analyze(self, n):
        env.calls = True
        self.args.analyze(n)
        env.regs = max(env.regs, len(self.args), n) # len(args) because args are copied e.g. A, B <- Reg(regs), Reg(regs+1). n because if no args
        env.args = max(env.args, len(self.args))
    def compile(self, n):
        self.args.compile(n)
        emit.call(self.id.name)
        if n > 0:
            emit.inst(Op.MOV, Reg(n), Reg.A)
        return Reg(n)
    
class If(Expr):
    def __init__(self, cond, state):
        self.cond, self.true, self.false = cond, state, None
    def analyze(self, n):
        self.cond.analyze(1)
        self.true.analyze(1)
        if self.false:
            self.false.analyze(1)
    def compile(self, n):
        env.if_jump_end = False
        label = env.next_label()
        sublabel = env.next_label() if self.false else label
        self.cond.compare(n, sublabel)
        self.true.compile(n)
        if self.false:
            if not (isinstance(self.true, Return) or (isinstance(self.true, Block) and self.true and isinstance(self.true[-1], Return))):
                emit.jump(Cond.JR, f'.L{label}')
                env.if_jump_end = True
            emit.labels.append(f'.L{sublabel}')
            self.false.branch(n, label)
        if env.if_jump_end:
            emit.labels.append(f'.L{label}')
    def branch(self, n, root):
        sublabel = env.next_label()
        self.cond.compare(n, sublabel)
        self.true.compile(n)
        if self.false:
            if not (isinstance(self.true, Return) or (isinstance(self.true, Block) and self.true and isinstance(self.true[-1], Return))):
                emit.jump(Cond.JR, f'.L{root}')
                env.if_jump_end = True
            emit.labels.append(f'.L{sublabel}')
            self.false.branch(n, root)

class While(Expr):
    def __init__(self, cond, state):
        self.cond, self.state = cond, state
    def analyze(self, n):
        self.cond.analyze(1)
        self.state.analyze(1)
    def compile(self, n):
        env.begin_loop()
        emit.labels.append(f'.L{env.loop.start()}')
        self.cond.compare(n, env.loop.end())
        self.state.compile(n)
        emit.jump(Cond.JR, f'.L{env.loop.start()}')
        emit.labels.append(f'.L{env.loop.end()}')
        env.end_loop()

class Do(Expr):
    def __init__(self, state, cond):
        self.state, self.cond = state, cond
    def analyze(self, n):        
        self.state.analyze(1)
        self.cond.analyze(1)
    def compile(self, n):
        env.begin_loop()
        emit.labels.append(f'.L{env.loop.start()}')        
        self.state.compile(n)
        self.cond.compare_false(n, env.loop.start())
        emit.labels.append(f'.L{env.loop.end()}')
        env.end_loop()

class For(While):
    def __init__(self, init, cond, step, state):
        super().__init__(cond, state)
        self.init, self.step = init, step
    def analyze(self, n):
        self.init.analyze(1)
        super().analyze(1)
        self.step.analyze(1)
    def compile(self, n):
        self.init.compile(n)
        env.begin_loop()
        emit.labels.append(f'.L{env.loop.start()}')
        self.cond.compare(n, env.loop.end())
        self.state.compile(n)
        self.step.compile(n)
        emit.jump(Cond.JR, f'.L{env.loop.start()}')
        emit.labels.append(f'.L{env.loop.end()}')
        env.end_loop()

class Continue(Expr):
    def compile(self, n):
        emit.jump(Cond.JR, f'.L{env.loop.start()}')
        
class Break(Expr):
    def compile(self, n):
        emit.jump(Cond.JR, f'.L{env.loop.end()}')

class Return(Expr):
    def __init__(self):
        self.expr = None
    def analyze(self, n):
        env.returns = True
        if self.expr:
            self.expr.analyze(1)
    def compile(self, n):
        if self.expr:
            self.expr.load(n)
        emit.jump(Cond.JR, f'.L{env.func}')
        
class Script(Expr):
    def __init__(self, id, sub):
        self.id, self.sub = id, sub
    def get_type(self):
        return self.id.get_type()
    def analyze(self, n):
        self.id.analyze(n)
        self.sub.analyze(n+1)
    def analyze_store(self, n):
        self.analyze(n+1)
    def dot(self, n):
        self.sub.compile(n)
    def address(self, n):
        self.id.compile(n)
        self.sub.load(n+1)
        if type(self.id.get_type()) is Array and self.id.get_type().of.size > 1:
            emit.inst(Op.MUL, Reg(n+1), self.id.get_type().of.size)
        emit.inst(Op.ADD, Reg(n), Reg(n+1))
        return Reg(n)
    def store(self, n):
        self.address(n+1)
        emit.store(Reg(n), Reg(n+1))     
    def compile(self, n):
        self.address(n)
        emit.load(Reg(n), Reg(n))
        return Reg(n)

class Arrow(Expr):
    def __init__(self, postfix, attr):
        self.postfix, self.attr = postfix, attr
    def get_type(self):
        return self.postfix.get_type().to[self.attr]
    def analyze(self, n):
        self.postfix.analyze(n)
    def analyze_store(self, n):
        self.analyze(n+1)
    def address(self, n):
        self.postfix.compile(n)
        emit.inst(Op.ADD, Reg(n), self.postfix.get_type().to.index(self.attr))
        return Reg(n)
    def store(self, n):
        emit.store(Reg(n), self.postfix.compile(n+1), self.postfix.get_type().to.index(self.attr), self.attr)
    def compile(self, n):        
        emit.load(Reg(n), self.postfix.compile(n), self.postfix.get_type().to.index(self.attr), self.attr)
        return Reg(n)

class Dot(Expr):
    def __init__(self, postfix, attr):
        self.postfix, self.attr = postfix, attr
    def get_type(self):
        return self.postfix.get_type()[self.attr]
    def analyze(self, n):
        self.postfix.analyze(n)
    def analyze_store(self, n):
        self.analyze(n+1)
    def address(self, n):
        emit.inst(Op.ADD, self.postfix.compile(n), self.postfix.get_type().index(self.attr))
        return Reg(n)
    def store(self, n):
        emit.store(Reg(n), self.postfix.address(n+1), self.postfix.get_type().index(self.attr), self.attr)
    def compile(self, n):        
        emit.load(Reg(n), self.postfix.address(n), self.postfix.get_type().index(self.attr), self.attr)
        return Reg(n)

class Global(Assign):
    def declare(self):
        env.globals.add(self.left.id.name)
    def compile(self):
        emit.glob(self.left.id.name, self.right.compile(0))

class Params(Expr, UserList):
    def analyze(self):
        for param in self:
            param.analyze(0)
    def compile(self):
        for i, param in enumerate(self):
            param.compile(0)
            emit.store(Reg(i), Reg.SP, env.scope.index(param.id.name))

class Block(Expr, UserList):
    def analyze(self, n):
        for statement in self:
            statement.analyze(n)
    def compile(self, n):
        env.begin_scope()
        for statement in self:
            statement.compile(env.args)
        env.end_scope()

class Func(Expr):
    def __init__(self, type_spec, id_, params, block):
        self.type_spec, self.id, self.params, self.block = type_spec, id_, params, block
    def declare(self):
        env.functions.append(self)
    def compile(self):
        env.begin_func()
        env.begin_scope()
        self.params.analyze()
        self.block.analyze(1)
        if env.returns:
            env.func = env.next_label()
        emit.labels.append(self.id.name)
        # print(env.args, env.regs)
        push = list(map(Reg, range(max(len(self.params), env.returns), env.args + env.regs)))
        emit.push(env.calls, *push)
        if env.space:
            emit.inst(Op.SUB, Reg.SP, env.space)
        self.params.compile()
        self.block.compile(env.args)
        if env.returns:
            emit.labels.append(f'.L{env.func}')
            if env.args > 0:
                emit.inst(Op.MOV, Reg.A, Reg(env.args))
        if env.space:
            emit.inst(Op.ADD, Reg.SP, env.space)
        emit.pop(env.calls, *push)
        if not env.calls:
            emit.ret()
        env.end_scope()

class Main(Expr):
    def __init__(self, block):
        self.block = block
    def declare(self):
        pass
    def compile(self):
        env.begin_func()
        env.begin_scope()
        self.block.analyze(1)
        if env.space:
            emit.inst(Op.SUB, Reg.SP, env.space)
        self.block.compile(0)
        if env.space:
            emit.inst(Op.ADD, Reg.SP, env.space)
        emit.halt()
        env.end_scope()

class Program(Expr, UserList):
    def compile(self):
        env.clear()
        emit.clear()
        for decl in self:
            decl.declare()
        for decl in self:
            decl.compile()
        return '\n'.join(emit.asm)