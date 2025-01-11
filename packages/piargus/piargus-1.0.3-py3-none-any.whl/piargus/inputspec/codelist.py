from pathlib import Path

import pandas as pd


class CodeList:
    """Describe a codelist for use with TauArgus.

    It can be used to attach labels to code lists.
    It only has effect when running TauArgus interactively.
    """

    @classmethod
    def from_cdl(cls, file):
        """Read cdl file."""
        df = pd.read_csv(file, index_col=0, header=None)
        codelist = CodeList(df.iloc[:, 0])
        if isinstance(file, (str, Path)):
            codelist.filepath = Path(file)

        return codelist

    def __init__(self, codes):
        """Create a codelist."""
        if hasattr(codes, 'keys'):
            self._codes = pd.Series(codes)
        else:
            self._codes = pd.Series(codes, index=codes)

        self._codes.index = self._codes.index.astype(str)
        self.filepath = None

    def __repr__(self):
        return f"{self.__class__.__name__}({self.to_dict()})"

    def __str__(self):
        return self.to_cdl()

    def __getitem__(self, key):
        """Get label of a code."""
        return self._codes[key]

    def __setitem__(self, key, value):
        """Set label of a code."""
        self._codes[key] = value

    def __iter__(self):
        return iter(self.keys())

    def __eq__(self, other):
        if hasattr(other, 'to_dict'):
            other = other.to_dict()

        return self.to_dict() == other

    @property
    def code_length(self) -> int:
        return max(map(len, self.iter_codes()))

    def keys(self):
        return self._codes.keys()

    def iter_codes(self):
        """Iterate through codes."""
        for code in self._codes.index:
            yield code

    def to_cdl(self, file=None, length=0):
        """Store codelist in cdl file."""
        codes = self._codes.copy()
        codes.index = codes.index.str.rjust(length)
        result = codes.to_csv(file, header=False)

        if isinstance(file, (str, Path)):
            self.filepath = Path(file)

        return result

    def to_dict(self):
        return self._codes.to_dict()
