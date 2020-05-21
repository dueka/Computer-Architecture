"""CPU functionality."""

import sys

# opcodes
HLT = 0b00000001
PRN = 0b01000111
LDI = 0b10000010
ADD = 0b10100000
MUL = 0b10100010
PUSH = 0b01000101
POP = 0b01000110
RET = 0b00010001
CALL = 0b01010000


class CPU:
    """Main CPU class."""

    def __init__(self):
        """Construct a new CPU."""
        self.ram = [0] * 256
        # registers to a list of 8 zeros
        self.reg = [0] * 8
        # set program counter to zero
        self.pc = 0
        self.halted = False
        self.reg[7] = 0xF4
        self.flag = 0
        self.inc_size = 1
        # self.reg[self.sp] = 0xF4
        self.branchtable = {}
        self.branchtable[LDI] = self.handle_LDI
        self.branchtable[PRN] = self.handle_PRN
        self.branchtable[HLT] = self.handle_HLT
        self.branchtable[MUL] = self.handle_MUL
        self.branchtable[ADD] = self.handle_ADD
        self.branchtable[PUSH] = self.handle_PUSH
        self.branchtable[POP] = self.handle_POP
        self.branchtable[RET] = self.handle_RET
        self.branchtable[CALL] = self.handle_CALL

    def load(self, filename):
        """Load a program into memory."""
        try:
            address = 0
            with open(filename) as f:
                for line in f:
                    comment_split = line.split('#')

                    num = comment_split[0].strip()

                    if num == '':
                        continue

                    val = int(num, 2)

                    self.ram_write(val, address)

                    address += 1
        except FileNotFoundError:
            print(f"{sys.argv[0]}: {filename} not found")
            sys.exit(2)

    def alu(self, op, reg_a, reg_b):
        """ALU operations."""

        if op in self.branchtable:
            self.branchtable[op](reg_a, reg_b)
        else:
            raise Exception("Unsupported ALU operation")

    def trace(self):
        """
        Handy function to print out the CPU state. You might want to call this
        from run() if you need help debugging.
        """

        print(f"TRACE: %02X | %02X %02X %02X |" % (
            self.pc,
            # self.fl,
            # self.ie,
            self.ram_read(self.pc),
            self.ram_read(self.pc + 1),
            self.ram_read(self.pc + 2)
        ), end='')

        for i in range(8):
            print(" %02X" % self.reg[i], end='')

        print()

    def ram_read(self, address):
        return self.ram[address]

    def ram_write(self, value, address):
        self.ram[address] = value

    def run(self):
        """Run the CPU."""
        while not self.halted:
            cmd = self.ram_read(self.pc)
            self.inc_size = 1
            operand_a = self.ram_read(self.pc + 1)
            operand_b = self.ram_read(self.pc + 2)
            covered_cmd = cmd & 0b001000000
            is_alu = covered_cmd >> 5
            moved_cmd = cmd >> 4
            sets_pc = moved_cmd & 0b0001

            if is_alu:
                self.alu(cmd, operand_a, operand_b)
            elif cmd in self.branchtable:
                self.branchtable[cmd](operand_a, operand_b)
            else:
                print(f"Invalid Instruction {cmd}")
                sys.exit(2)

            if not sets_pc:
                self.inc_size += cmd >> 6
                self.pc += self.inc_size

    def handle_HLT(self, opr1, opr2):
        # self.halted = True
        sys.exit(0)

    def handle_PRN(self, opr1, opr2):
        # reg_index = opr1
        num = self.reg[opr1]
        print(num)
        # inc_size = 2

    def handle_LDI(self, opr1, opr2):
        self.reg[opr1] = opr2

    def handle_ADD(self, reg_a, reg_b):
        self.reg[reg_a] += self.reg[reg_b]

    def handle_MUL(self, reg_a, reg_b):
        self.reg[reg_a] *= self.reg[reg_b]

    def handle_PUSH(self, opr1, opr2):
        self.reg[7] -= 1
        num = self.reg[opr1]
        self.ram_write(num, self.reg[7])

    def handle_POP(self, opr1, opr2):
        num = self.ram_read(self.reg[7])
        self.reg[opr1] = num
        self.reg[7] += 1

    def handle_RET(self, opr1, opr2):
        return_address = self.ram_read(self.reg[7])
        self.reg[7] += 1
        self.pc = return_address

    def handle_CALL(self, opr1, opr2):
        self.reg[7] -= 1
        self.ram_write(self.pc + 2, self.reg[7])
        num = self.reg[opr1]
        self.pc = num
