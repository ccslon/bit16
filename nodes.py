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
        self._labels = 0
        self.loop = Loop()
        self.structs = {}
        self.locals = SetList()
        self.functions = []
    def reset_scope(self):
        self.func = None
        self.locals.clear()
        self.args = 0
        self.regs = 0
        self.returns = False             
    def start_loop(self):
        self.loop.append((self.next_label(), self.next_label()))
    def end_loop(self):
        self.loop.pop()
    def next_label(self):
        label = self._labels
        self._labels += 1
        return label

class Traveler:
    def __init__(self):
        self.env = Env()
        self.labels = []
        self.rom = []
    def print_ASM(self, asm):
        for label in self.labels:
            print(f'{label}:')
        print(f'  {asm}')
    def push(self, *regs):
        self.print_ASM('PSH '+', '.join(reg.name for reg in regs))
        for reg in regs:
            self.add(Inst2, (Op.SUB, Reg.SP, 1))
            self.add(Load1, (True, reg, Reg.SP, 0))
    def pop(self, *regs):
        self.print_ASM('POP '+', '.join(reg.name for reg in regs))
        for reg in reversed(regs):
            self.add(Inst2, (Op.ADD, Reg.SP, 1))
            self.add(Load1, (False, reg, Reg.SP, -1))
    def call(self, label):
        self.print_ASM(f'CALL {label}')
        self.add(Inst1, (Op.MOV, Reg.LR, Reg.PC ))
        self.add(Inst2, (Op.ADD, Reg.LR, 3))
        self.add(Jump, (Cond.JMP, label))
    def load1(self, storing, rd, rb, offset5):
        if storing:
            self.print_ASM(f'LD [{rb.name}, {offset5}], {rd.name}')
        else:
            self.print_ASM(f'LD {rd.name}, [{rb.name}, {offset5}]')
        self.add(Load1, (storing, rd, rb, offset5))
    def inst(self, inst, op, rd, src):
        if inst is Inst1:
            self.print_ASM(f'{op.name} {rd.name}, {src.name}')
        elif inst is Inst2:
            self.print_ASM(f'{op.name} {rd.name}, {src}')
        self.add(inst, (op, rd, src))
    def inst4(self, op, rd, rs, rs2):
        self.print_ASM(f'{op.name} {rd.name}, {rs.name}, {rs2.name}')
        self.add(Inst4, (op, rd, rs, rs2))
    def inst5(self, op, rd):
        self.print_ASM(f'{op.name} {rd.name}')
        self.add(Inst5, (op, rd))
    def jump(self, cond, target):
        self.print_ASM(f'{cond.name} {target}')
        self.add(Jump, (cond, target))
    def halt(self):
        self.print_ASM('HALT')
        self.add(Inst1, (Op.MOV, Reg.PC, Reg.PC))
    def add(self, inst, args):
        self.rom.append((self.labels, inst, args))
        self.labels = []

class Expr:
    INST = Inst1
    def load(self, trav, n):
        self.compile(trav, n)
    def branch(self, trav, n, _):
        self.compile(trav, n)
    def compare(self, trav, n, label):
        trav.inst(Inst2, Op.CMP, (self.compile(trav, n), 0))
        trav.jump(Cond.JMP, f'.L{label}')
    def analyze(self, trav, n):
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
    def load(self, trav, n):
        trav.inst(Inst2, Op.MOV, Reg(n), self.value)
    def compile(self, trav, n):
        return self.value
    def __str__(self):
        return f"{self.__class__.__name__}({self.value})"
    
class Var(Expr):
    def __init__(self, name):
        self.name = name
    def analyze(self, trav, n):
        if self.name not in trav.env.locals:
            trav.env.locals.append(self.name)
        trav.env.regs = max(trav.env.regs, n)
    def address(self, trav, n):
        trav.inst4(Op.ADD, Reg(n), Reg.SP, trav.env.locals.index(self.name))
        return Reg(n)
    def store(self, trav, n):
        trav.load1(True, Reg(n), Reg.SP, trav.env.locals.index(self.name))
    def compile(self, trav, n):
        trav.load1(False, Reg(n), Reg.SP, trav.env.locals.index(self.name))
        return Reg(n)
    def __str__(self):
        return f"{self.__class__.__name__}('{self.name}')"    

class Address(Expr):
    def __init__(self, unary):
        self.unary = unary
    def analyze(self, trav, n):
        self.unary.analyze(trav, n)
    def compile(self, trav, n):
        self.unary.address(trav, n)
    def __str__(self):
        return f'{self.__class__.__name__}({self.unary})'

class Pointer(Expr):
    def __init__(self, unary):
        self.unary = unary
    def analyze(self, trav, n):
        self.unary.analyze(trav, n)
    def store(self, trav, n):
        self.unary.compile(trav, n+1)
        trav.load1(True, Reg(n), Reg(n+1), 0)
    def compile(self, trav, n):
        self.unary.compile(trav, n)
        trav.load1(False, Reg(n), Reg(n))
        return Reg(n)
    def __str__(self):
        return f'{self.__class__.__name__}({self.unary})'

class Unary(Expr):
    OPS = {'-':Op.NEG,
           'not':Op.NOT}     
    def __init__(self, sign, primary):
        self.sign, self.primary = self.OPS[sign], primary
    def analyze(self, trav, n):
        self.primary.analyze(trav, n)
    def compile(self, trav, n):
        trav.inst5(self.sign, self.primary.compile(trav, n))
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
    def analyze(self, trav, n):
        self.left.analyze(trav, n)
        self.right.analyze(trav, n+1)
    def compile(self, trav, n):
        trav.inst(self.right.INST, self.op, self.left.compile(trav, n), self.right.compile(trav, n+1))
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
        trav.inst(self.right.INST, Op.CMP, self.left.compile(trav, n), self.right.compile(trav, n+1))
        trav.jump(self.INV[self.op], f'.L{label}')

class Logic(Binary):
    def __init__(self, op, left, right):
        self.op, self.left, self.right = op, left, right
    def compare(self, trav, n, label):
        if self.op == 'and':
            trav.inst(Inst2, Op.CMP, self.left.compile(trav, n), 0)
            trav.jump(Cond.JEQ, f'.L{label}')
            trav.inst(Inst2, Op.CMP, self.right.compile(trav, n), 0)
            trav.jump(Cond.JEQ, f'.L{label}')
        elif self.op == 'or':
            sublabel = trav.env.next_label()
            trav.inst(Inst2, Op.CMP, self.left.compile(trav, n), 0)
            trav.jump(Jump, (Cond.JNE, f'.L{sublabel}'))
            trav.inst(Inst2, Op.CMP, self.right.compile(trav, n), 0)
            trav.jump(Cond.JEQ, f'.L{label}')
            trav.labels.append(f'.L{sublabel}')

class Assign(Expr):
    def __init__(self, left, right):
        self.left, self.right = left, right
    def analyze(self, trav, n):
        self.right.analyze(trav, n)
        self.left.analyze(trav, n+1 if isinstance(self.left, (Attr, Script, Pointer)) else n)
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
                trav.inst(Inst1, Op.MOV, Reg(i), Reg(n+i))
    def __str__(self):
        return f'{self.__class__.__name__}({",".join(map(str,self))})'  

class Call(Expr):
    def __init__(self, var, args):
        self.var, self.args = var, args
    def analyze(self, trav, n):
        self.args.analyze(trav, n)
        trav.env.regs = max(trav.env.regs, len(self.args), n)
        trav.env.args = max(trav.env.args, len(self.args))
    def compile(self, trav, n):
        self.args.compile(trav, n)
        trav.call(self.var.name)
        if n > 0:
            trav.inst(Inst1, Op.MOV, Reg(n), Reg.A)
        return Reg(n)
    def __str__(self):
        return f'{self.__class__.__name__}({self.var},{self.args})'
    
class If(Expr):
    def __init__(self, cond, state):
        self.cond, self.true, self.false = cond, state, None
    def analyze(self, trav, n):
        self.cond.analyze(trav, 1)
        self.true.analyze(trav, 1)
        if self.false:
            self.false.analyze(trav, 1)
    def compile(self, trav, n):
        label = trav.env.next_label()
        sublabel = trav.env.next_label() if self.false else label
        self.cond.compare(trav, n, sublabel)
        self.true.compile(trav, n)
        if self.false:
            trav.jump(Cond.JMP, f'.L{label}')
            trav.labels.append(f'.L{sublabel}')
            self.false.branch(trav, n, label)
        trav.labels.append(f'.L{label}')
    def branch(self, trav, n, root):
        sublabel = trav.env.next_label()
        self.cond.compare(trav, n, sublabel)
        self.true.compile(trav, n)
        trav.jump(Cond.JMP, f'.L{root}')
        trav.labels.append(f'.L{sublabel}')
        if self.false:
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
        trav.env.start_loop()
        trav.labels.append(f'.L{trav.env.loop.start()}')
        self.cond.compare(trav, n, trav.env.loop.end())
        self.state.compile(trav, n)
        trav.jump(Cond.JMP, f'.L{trav.env.loop.start()}')
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
        trav.env.start_loop()
        trav.labels.append(f'.L{trav.env.loop.start()}')
        self.cond.compare(trav, n, trav.env.loop.end())
        self.state.compile(trav, n)
        self.step.compile(trav, n)
        trav.jump(Cond.JMP, f'.L{trav.env.loop.start()}')
        trav.labels.append(f'.L{trav.env.loop.end()}')
        trav.env.end_loop()
    def __str__(self):
        return f'{self.__class__.__name__}({self.init},{self.cond},{self.step},{self.state})'

class Continue(Expr):
    def compile(self, trav, n):
        trav.jump(Cond.JMP, f'.L{trav.env.loop.start()}')
        
class Break(Expr):
    def compile(self, trav, n):
        trav.jump(Cond.JMP, f'.L{trav.env.loop.end()}')

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
        trav.jump(Cond.JMP, f'.L{trav.env.func}')
    def __str__(self):
        return f"{self.__class__.__name__}({self.expr})"
        
class Script(Expr):
    def __init__(self, var, sub):
        self.var, self.sub = var, sub
    def analyze(self, trav, n):
        self.var.analyze(trav, n)
        self.sub.analyze(trav, n+1)
    def address(self, trav, n):
        self.var.compile(trav, n)
        self.sub.compile(trav, n+1)
        trav.inst(Inst1, Reg(n), Reg(n+1))
    def store(self, trav, n):
        self.address(trav, n+1)
        trav.load1(True, Reg(n), Reg(n+1), 0)
    def compile(self, trav, n):
        self.address(trav, n)
        trav.load1(False, Reg(n), Reg(n), 0)
        return Reg(n)
    def __str__(self):
        return f'{self.__class__.__name__}({self.var},{self.sub})'

class Attr(Expr):
    def __init__(self, var, attr):
        self.var, self.attr = var, attr
    def analyze(self, trav, n):
        self.var.analyze(trav, n)
    def address(self, trav, n):
        self.var.compile(trav, n)
        trav.inst(Inst2, Op.ADD, Reg(n), trav.env.structs[self.attr])
    def store(self, trav, n):
        self.address(trav, n+1)
        trav.load1(True, Reg(n), Reg(n+1), 0)
    def compile(self, trav, n):
        self.address(trav, n)
        trav.load1(False, Reg(n), Reg(n), 0)
    def __str__(self):
        return f'{self.__class__.__name__}({self.var},{self.attr})'

class Fields(Expr, UserList):
    def declare(self, trav):
        for i, field in enumerate(self):
            trav.env.structs[field.name] = i   
    def __str__(self):
        return f'{self.__class__.__name__}({",".join(map(str,self))})'  

class Struct(Expr):
    def __init__(self, var, fields):
        self.var, self.fields = var, fields
    def declare(self, trav):
        self.fields.declare(trav)
    def compile(self, trav):
        pass
    def __str__(self):
        return f'{self.__class__.__name__}({self.var},{self.fields})'

class Params(Expr, UserList):
    def analyze(self, trav):
        for param in self:
            trav.env.locals.add(param.name)
    def compile(self, trav):
        for i, param in enumerate(self):
            trav.load1(True, Reg(i), Reg.SP, trav.env.locals.index(param.name))
    def __str__(self):
        return f'{self.__class__.__name__}({",".join(map(str,self))})'

class Block(Expr, UserList):
    def analyze(self, trav, n):
        for statement in self:
            statement.analyze(trav, n)
    def compile(self, trav, n):
        for statement in self:
            statement.compile(trav, trav.env.args)
    def __str__(self):
        nl = ",\n"
        return f'{self.__class__.__name__}(\n{nl.join(map(str,self))}\n)'

class Func(Expr):
    def __init__(self, var, params, block):
        self.var, self.params, self.block = var, params, block
    def declare(self, trav):
        trav.env.functions.append(self)
    def compile(self, trav):
        trav.env.reset_scope()
        self.params.analyze(trav)
        self.block.analyze(trav, 0)
        if trav.env.returns:
            trav.env.func = trav.env.next_label()
        trav.labels.append(self.var.name)
        #print(trav.env.args, trav.env.regs)
        push = list(map(Reg, range(max(len(self.params), trav.env.returns), trav.env.args + trav.env.regs)))
        trav.push(Reg.LR, *push)
        if trav.env.locals:
            trav.inst(Inst2, Op.SUB, Reg.SP, len(trav.env.locals))
        self.params.compile(trav)
        self.block.compile(trav, trav.env.args)
        if trav.env.returns:
            trav.labels.append(f'.L{trav.env.func}')
            if trav.env.args > 0:
                trav.inst(Inst1, Op.MOV, Reg.A, Reg(trav.env.args))
        if trav.env.locals:
            trav.inst(Inst2, Op.ADD, Reg.SP, len(trav.env.locals))
        trav.pop(Reg.PC, *push)
        
    def __str__(self):
        return f'{self.__class__.__name__}({self.var},{self.params},{self.block})'

class Main(Expr):
    def __init__(self, block):
        self.block = block
    def declare(self, trav):
        pass
    def compile(self, trav):
        trav.env.reset_scope()
        self.block.analyze(trav, 0)
        self.block.compile(trav, 0)
        trav.halt()

class Program(Expr, UserList):
    def compile(self):
        trav = Traveler()
        for decl in self:
            decl.declare(trav)
        for decl in self:
            decl.compile(trav)
        return trav.rom
    def __str__(self):
        nl = ",\n"
        return f'{self.__class__.__name__}(\n{nl.join(map(str,self))}\n)'