import subprocess

WRONG_ANSWER = 0
CORRECT = 1
PRESENTATION_ERROR = 2

class Checker:
    def check(self, infile_ignored, outfile, refout):
        exact_checked = False
        try:
            args = ['/usr/bin/cmp', '--silent', outfile.name, refout.name]
            code = subprocess.call(args, stdout=subprocess.DEVNULL)
            if code == 0:
                return CORRECT
            exact_checked = True
        except FileNotFoundError:
            pass
        out = outfile.read()
        ref = refout.read()
        if not exact_checked and out == ref:
            return CORRECT
        ref_lines = self.trim_whitespace(ref.splitlines())
        out_lines = self.trim_whitespace(out.splitlines())
        return PRESENTATION_ERROR if ref_lines == out_lines else WRONG_ANSWER

    def trim_whitespace(self, lines):
        lines = [line.rstrip() for line in lines]
        while lines and not lines[-1].strip():
            lines.pop()
        return lines
