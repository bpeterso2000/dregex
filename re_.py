import re
import _sre
import sre_parse
import sre_compile
from sre_constants import SRE_FLAG_DEBUG

# import _sre_.py


class RegEx:

    def __init__(self, pattern, flags=0):
        self.flags = flags | SRE_FLAG_DEBUG
        self.pattern = pattern
        self.compile()

    @property
    def dis(self):
        """Show formatted opcodes."""
        return sre_compile.dis(self.code)

    @property
    def dump(self):
        """Show formatted pattern codes."""
        return self.subpattern.dump()

    def compile(self):
        self.subpattern = sre_parse.parse(self.pattern, self.flags)
        self.code = sre_compile._code(self.subpattern, self.flags)

        self.groupindex = self.subpattern.pattern.groupdict
        self.indexgroup = [None] * self.subpattern.pattern.groups
        for k, i in self.groupindex.items():
            self.indexgroup[i] = k

        self.regex = _sre.compile(
            self.pattern,
            self.flags | self.subpattern.pattern.flags,
            self.code,
            self.subpattern.pattern.groups-1,
            self.groupindex, tuple(self.indexgroup)
        )


def compile(pattern, flags=0):
    return RegEx(pattern, flags)
