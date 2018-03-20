import _sre
import sre_parse
import sre_compile
from sre_constants import SRE_FLAG_DEBUG

import _sre_


class RegEx:

    def __init__(self, pattern, flags=0):
        self.flags = flags
        self.pattern = pattern
        self.debug = True
        self.compile()

    @property
    def dis(self):
        """Show formatted opcodes."""
        sre_compile.dis(self.code)

    @property
    def dump(self):
        """Show formatted pattern codes."""
        return self.subpattern.dump()

    def compile(self):
        self.subpattern = sre_parse.parse(self.pattern, self.flags)
        self.code = sre_compile._code(self.subpattern, self.flags)

        # groups=0, groupindex={}, indexgroup=[None]
        self.groupindex = self.subpattern.pattern.groupdict
        self.indexgroup = [None] * self.subpattern.pattern.groups
        for k, i in self.groupindex.items():
            self.indexgroup[i] = k

        module = _sre_ if self.debug else _sre
        self.regex = getattr(module, 'compile')(
            self.pattern,
            self.flags | self.subpattern.pattern.flags,
            self.code,
            self.subpattern.pattern.groups - 1,
            self.groupindex, tuple(self.indexgroup)
        )
        self.dump
        print('-' * 76)
        self.dis

    def search(self, string):
        return self.regex.search(string)


def compile(pattern, flags=0):
    return RegEx(pattern, flags)


def search(pattern, text, flags=0):
    r = RegEx(pattern, flags)
    r.search(text)
