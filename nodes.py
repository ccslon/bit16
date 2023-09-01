# -*- coding: utf-8 -*-
"""
Created on Mon Jul  3 19:48:36 2023

@author: Colin
"""
from collections import UserList
from bit16 import Reg, Op, Cond, Inst1, Inst2, Inst4, Inst5, Load1, Jump

class Loop(UserList):
    def start(self):
        return self[-1][0]
    def end(self):
        return self[-1][1]

class SetList(UserList):
    def add(self, item):
        if item not in self:
            self.append(item)

class Env:
    def __init__(self):
        self.labels = 0
        self.current = None
        self.loop = Loop()
        self.structs = {}
        self.rom = []
        self.locals = SetList()
        self.globals = SetList()
    def reset(self):
        self.call = None
        self.locals.clear()
        self.max_args = 0
        self.max_regs = 0
        self.returns = False
    def add(self, inst, args):
        self.rom.append((self.current, inst, args))
        self.current = None            
    def start_loop(self):
        self.loop.append((self.next_label(), self.next_label()))
    def end_loop(self):
        self.loop.pop()
    def next_label(self):
        label = self.labels
        self.labels += 1
        return label

class Expr:
    INST = Inst1
    def load(self, env, n):
        self.compile(env, n)
    def branch(self, env, n, _):
        self.compile(env, n)
    def compare(self, env, n, label):
        env.add(Inst2, (self.compile(env, n), 0))
        env.add(Jump, (Cond.JMP, f'.L{label}'))
    def analyze(self, env, n):
        pass
    def __str__(self):
        return f'{self.__class__.__name__}()'
    
class Const(Expr):
    INST = Inst2
    def __init__(self, value):
        if value == 'true':
            value = 1
        elif value in ['false','null']:
            value = 0
        self.value = int(value)
    def load(self, env, n):
        env.add(Inst2, (Op.MOV, Reg(n), self.value))
    def compile(self, env, n):
        return self.value
    def __str__(self):
        return f"{self.__class__.__name__}({self.value})"
    
class Var(Expr):
    def __init__(self, name):
        self.name = name
    def analyze(self, env, n):
        if self.name not in env.locals and self.name not in env.globals:
            env.locals.append(self.name)
        env.max_regs = max(env.max_regs, n)
    def address(self, env, n):
        env.add(Inst4, (Op.ADD, Reg(n), Reg.SP, env.locals.index(self.name)))
        return Reg(n)
    def store(self, env, n):
        env.add(Load1, (True,Reg(n),Reg.SP,env.locals.index(self.name)))
    def compile(self, env, n):
        env.add(Load1, (False,Reg(n),Reg.SP,env.locals.index(self.name))) 
        return Reg(n)
    def __str__(self):
        return f"{self.__class__.__name__}('{self.name}')"    

class Address(Expr):
    def __init__(self, unary):
        self.unary = unary
    def analyze(self, env, n):
        self.unary.analyze(env, n)
    def compile(self, env, n):
        self.unary.address(env, n)
    def __str__(self):
        return f'{self.__class__.__name__}({self.unary})'

class Pointer(Expr):
    def __init__(self, unary):
        self.unary = unary
    def analyze(self, env, n):
        self.unary.analyze(env, n)
    def store(self, env, n):
        self.unary.compile(env, n+1)
        env.add(Load1, (True, Reg(n), Reg(n+1), 0))
    def compile(self, env, n):
        self.unary.compile(env, n)
        env.add(Load1, (False, Reg(n), Reg(n)))
        return n
    def __str__(self):
        return f'{self.__class__.__name__}({self.unary})'

class Unary(Expr):
    OPS = {'-':Op.NEG,
           'not':Op.NOT}     
    def __init__(self, sign, primary):
        self.sign, self.primary = self.OPS[sign], primary
    def analyze(self, env, n):
        self.primary.analyze(env, n)
    def compile(self, env, n):
        env.add(Inst5, (self.sign, self.primary.compile(env, n)))
        return Reg(n)
    def __str__(self):
        return f'{self.sign[0].upper() + self.sign[1:]}({self.primary})'

class Binary(Expr):    
    OPS = {'+' :Op.ADD,
           '-' :Op.SUB,
           '*' :Op.MUL,
           '<<':Op.SHL,
           '>>':Op.SHR,
           '|' :Op.OR,
           '&' :Op.AND,
           '^' :Op.XOR}
    def __init__(self, op, left, right):
        self.op, self.left, self.right = self.OPS[op], left, right
    def analyze(self, env, n):
        self.left.analyze(env, n)
        self.right.analyze(env, n+1)
    def compile(self, env, n):
        env.add(self.right.INST, (self.op, self.left.compile(env, n), self.right.compile(env, n+1)))
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
    def compare(self, env, n, label):
        env.add(self.right.INST, (Op.CMP, self.left.compile(env, n), self.right.compile(env, n+1)))
        env.add(Jump, (self.INV[self.op], f'.L{label}'))

class Logic(Binary):
    def __init__(self, op, left, right):
        self.op, self.left, self.right = op, left, right
    def compare(self, env, n, label):
        if self.op == 'and':
            env.add(Inst2, (Op.CMP, self.left.compile(env, n), 0))
            env.add(Jump, (Cond.JEQ, f'.L{label}'))
            env.add(Inst2, (Op.CMP, self.right.compile(env, n), 0))
            env.add(Jump, (Cond.JEQ, f'.L{label}'))
        elif self.op == 'or':
            sublabel = env.next_label()
            env.add(Inst2, (Op.CMP, self.left.compile(env, n), 0))
            env.add(Jump, (Cond.JNE, f'.L{sublabel}'))
            env.add(Inst2, (Op.CMP, self.right.compile(env, n), 0))
            env.add(Jump, (Cond.JEQ, f'.L{label}'))
            env.current = f'.L{sublabel}'

class Assign(Expr):
    def __init__(self, left, right):
        self.left, self.right = left, right
    def analyze(self, env, n):
        self.right.analyze(env, n)
        self.left.analyze(env, n+1 if isinstance(self.left, (Attr, Script, Pointer)) else n)
    def compile(self, env, n):
        self.right.load(env, n)
        self.left.store(env, n)
        return Reg(n)
    def __str__(self):
        return f'{self.__class__.__name__}({self.left},{self.right})'

class Args(Expr, UserList):
    def analyze(self, env, n):        
        for i, arg in enumerate(self, n):
            arg.analyze(env, i)
    def compile(self, env, n):
        for i, arg in enumerate(self, n):
            arg.load(env, i)
        if n > 0:
            for i, arg in enumerate(self):
                env.add(Inst1, (Op.MOV, Reg(i), Reg(n+i)))
    def __str__(self):
        return f'{self.__class__.__name__}({",".join(map(str,self))})'  

class Call(Expr):
    def __init__(self, var, args):
        self.var, self.args = var, args
    def analyze(self, env, n):
        self.args.analyze(env, n)
        env.max_regs = max(env.max_regs, len(self.args), n)
        env.max_args = max(env.max_args, len(self.args))
    def compile(self, env, n):
        self.args.compile(env, n)
        env.add(Inst1, (Op.MOV, Reg.LR, Reg.PC))
        env.add(Inst2, (Op.ADD, Reg.LR, 3))
        env.add(Jump, (Cond.JMP, self.var.name))
        if n > 0:
            env.add(Inst1, (Op.MOV, Reg(n), Reg.A))
        return Reg(n)
    def __str__(self):
        return f'{self.__class__.__name__}({self.var},{self.args})'
    
class If(Expr):
    def __init__(self, cond, state):
        self.cond, self.true, self.false = cond, state, None
    def analyze(self, env, n):
        self.cond.analyze(env, 1)
        self.true.analyze(env, 1)
        if self.false:
            self.false.analyze(env, 1)
    def compile(self, env, n):
        label = env.next_label()
        sublabel = env.next_label() if self.false else label
        self.cond.compare(env, n, sublabel)
        self.true.compile(env, n)
        if self.false:
            env.add(Jump, (Cond.JMP, f'.L{label}'))
            env.current = f'.L{sublabel}'
            self.false.branch(env, n, label)
        env.current = f'.L{label}'
    def branch(self, env, n, root):
        sublabel = env.next_label()
        self.cond.compare(env, n, sublabel)
        self.true.compile(env, n)
        env.add(Jump, (Cond.JMP, f'.L{root}'))
        env.current = f'.L{sublabel}'
        if self.false:
            self.false.branch(env, n, root)
    def __str__(self):
        return f'{self.__class__.__name__}({self.cond},{self.true},{self.false})'

class While(Expr):
    def __init__(self, cond, state):
        self.cond, self.state = cond, state
    def analyze(self, env, n):
        self.cond.analyze(env, 1)
        self.state.analyze(env, 1)
    def compile(self, env, n):
        env.start_loop()
        env.current = f'.L{env.loop.start()}'
        self.cond.compare(env, n, env.loop.end())
        self.state.compile(env, n)
        env.add(Jump, (Cond.JMP, f'.L{env.loop.start()}'))
        env.current = f'.L{env.loop.end()}'
        env.end_loop()
    def __str__(self):
        return f'{self.__class__.__name__}({self.cond},{self.state})'
        
class For(While):
    def __init__(self, init, cond, step, state):
        super().__init__(cond, state)
        self.init, self.step = init, step
    def analyze(self, env, n):
        self.init.analyze(env, 1)
        super().analyze(env, 1)
        self.step.analyze(env, 1)
    def compile(self, env, n):
        self.init.compile(env, n)
        env.start_loop()
        env.current = f'.L{env.loop.start()}'
        self.cond.compare(env, n, env.loop.end())
        self.state.compile(env, n)
        self.step.compile(env, n)
        env.add(Jump, (Cond.JMP, f'.L{env.loop.start()}'))
        env.current = f'.L{env.loop.end()}'
        env.end_loop()
    def __str__(self):
        return f'{self.__class__.__name__}({self.init},{self.cond},{self.step},{self.state})'

class Continue(Expr):
    def compile(self, env, n):
        env.add(Jump, (Cond.JMP, f'.L{env.loop.start()}'))
        
class Break(Expr):
    def compile(self, env, n):
        env.add(Jump, (Cond.JMP, f'.L{env.loop.end()}'))

class Return(Expr):
    def __init__(self):
        self.expr = None
    def analyze(self, env, n):
        env.returns = True
        if self.expr:
            self.expr.analyze(env, 1)
    def compile(self, env, n):
        if self.expr:
            self.expr.load(env, n)
        env.add(Jump, (Cond.JMP, f'.L{env.call}'))
    def __str__(self):
        return f"{self.__class__.__name__}({self.expr})"
        
class Script(Expr):
    def __init__(self, var, sub):
        self.var, self.sub = var, sub
    def analyze(self, env, n):
        self.var.analyze(env, n)
        self.sub.analyze(env, n+1)
    def address(self, env, n):
        self.var.compile(env, n)
        self.sub.compile(env, n+1)
        env.add(Inst1, (Reg(n), Reg(n+1)))
    def store(self, env, n):
        self.address(env, n+1)
        env.add(Load1, (True, Reg(n), Reg(n+1), 0))
    def compile(self, env, n):
        self.address(env, n)
        env.add(Load1, (False, Reg(n), Reg(n), 0))
        return Reg(n)
    def __str__(self):
        return f'{self.__class__.__name__}({self.var},{self.sub})'

class Attr(Expr):
    def __init__(self, var, attr):
        self.var, self.attr = var, attr
    def analyze(self, env, n):
        self.var.analyze(env, n)
    def address(self, env, n):
        self.var.compile(env, n)
        env.add(Inst2, (Op.ADD, Reg(n), env.structs[self.attr]))
    def store(self, env, n):
        self.address(env, n+1)
        env.add(Load1, (True, Reg(n), Reg(n+1), 0))
    def compile(self, env, n):
        self.address(env, n)
        env.add(Load1, (False, Reg(n), Reg(n), 0))
    def __str__(self):
        return f'{self.__class__.__name__}({self.var},{self.attr})'

class Fields(Expr, UserList):
    def declare(self, env):
        for i, field in enumerate(self):
            env.structs[field.name] = i   
    def __str__(self):
        return f'{self.__class__.__name__}({",".join(map(str,self))})'
    
class Global(Assign):
    def declare(self, env):
        env.globals.add(self.left.name)
    def compile(self, env):
        print(f'{self.left.name}: {self.right.value}')    

class Struct(Expr):
    def __init__(self, var, fields):
        self.var, self.fields = var, fields
    def declare(self, env):
        self.fields.declare(env)
    def compile(self, env):
        pass
    def __str__(self):
        return f'{self.__class__.__name__}({self.var},{self.fields})'

class Params(Expr, UserList):
    def analyze(self, env):
        for param in self:
            env.locals.add(param.name)
    def compile(self, env):
        for i, param in enumerate(self):
            env.add(Load1, (True, Reg(i), Reg.SP, env.locals.index(param.name)))
    def __str__(self):
        return f'{self.__class__.__name__}({",".join(map(str,self))})'

class Block(Expr, UserList):
    def analyze(self, env, n):
        for statement in self:
            statement.analyze(env, n)
    def compile(self, env, n):
        for statement in self:
            statement.compile(env, env.max_args)
    def __str__(self):
        nl = ",\n"
        return f'{self.__class__.__name__}(\n{nl.join(map(str,self))}\n)'

class Func(Expr):
    def __init__(self, var, params, block):
        self.var, self.params, self.block = var, params, block
    def declare(self, env):
        pass
    def compile(self, env):
        env.reset()
        self.params.analyze(env)
        self.block.analyze(env, 0)
        if env.returns:
            env.call = env.next_label()
        env.current = self.var.name
        #print(env.max_args, env.max_regs)
        pushed = list(range(max(len(self.params), env.returns), env.max_args + env.max_regs))
        env.add(Inst2, (Op.SUB, Reg.SP, 1))
        env.add(Load1, (True, Reg.LR, Reg.SP, 0))
        for reg in pushed:
            env.add(Inst2, (Op.SUB, Reg.SP, 1))
            env.add(Load1, (True, Reg(reg), Reg.SP, 0))

        if len(env.locals):
            env.add(Inst2, (Op.SUB, Reg.SP, len(env.locals)))
        self.params.compile(env)
        self.block.compile(env, env.max_args)
        if env.returns:
            env.current = f'.L{env.call}'
            if env.max_args > 0:
                env.add(Inst1, (Op.MOV, Reg.A, R(env.max_args)))
        if len(env.locals):
            env.add(Inst2, (Op.ADD, Reg.SP, len(env.locals)))
        for reg in reversed(pushed):
            env.add(Inst2, (Op.ADD, Reg.SP, 1))
            env.add(Load1, (False, Reg(reg), Reg.SP, -1))
        env.add(Inst2, (Op.ADD, Reg.SP, 1)) 
        env.add(Load1, (False, Reg.PC, Reg.SP, -1))
    def __str__(self):
        return f'{self.__class__.__name__}({self.var},{self.params},{self.block})'

class Program(Expr, UserList):
    def compile(self):
        env = Env()
        for decl in self:
            decl.declare(env)
        for decl in self:
            decl.compile(env)
        return env.rom
    def __str__(self):
        nl = ",\n"
        return f'{self.__class__.__name__}(\n{nl.join(map(str,self))}\n)'