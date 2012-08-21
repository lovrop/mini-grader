class DiffChecker:
    '''Simple diff between expected and received output, ignoring trailing whitespace'''
    def correct(self, infile_ignored, outfile, refout):
        outfile.seek(0)
        ref_lines = self.trim_whitespace(refout.readlines())
        out_lines = self.trim_whitespace(outfile.readlines())
        return ref_lines == out_lines

    def trim_whitespace(self, lines):
        lines = [line.rstrip() for line in lines]
        while lines and not lines[-1].strip():
            lines.pop()
        return lines
