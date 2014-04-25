import json
import logging
import sys

from blessings import Terminal

log = logging.getLogger('reporter')


class _O(dict):
    def __getattr__(self, k):
        return self[k]


class Reporter(object):
    status_flags = {
        0: 'PASS',
        -1: 'ERROR',
        1: 'ERROR',
        None: 'FAIL'
    }

    def __init__(self, fp=sys.stdout, options=None):
        self.fp = fp
        self.options = options
        self.messages = []
        self.term = Terminal()

    def emit(self, msg):
        """Emit a single record to output fp"""
        self.messages.append(_O(msg))

    def header(self):
        pass

    def _calculate(self):
        total_seconds = 0
        by_code = {}
        for m in self.messages:
            total_seconds += m.get('duration', 0)
            ec = m['returncode']
            ec_ct = by_code.get(ec,  0)
            by_code[ec] = ec_ct + 1
        return total_seconds, by_code

    def write(self, s, *args, **kwargs):
        kwargs['t'] = self.term
        self.fp.write(s.format(*args, **kwargs))

    def report_errors(self, by_code):
        if len(by_code.keys()) > 1 or 0 not in by_code:
            for m in self.messages:
                if m['returncode'] == 0:
                    continue
                self.fp.write('-' * 78 + '\n')
                if m.get('suite'):
                    self.write('{t.bold}{t.red}{m.suite}{t.normal}::', m=m)
                self.write("{t.bold}{t.red}{m.test}{t.normal}\n", m=m)
                self.write("[{t.cyan}{m.exit:<30}{t.normal} exited"
                           " {t.red}{m.returncode}{t.normal}]\n", m=m)
                self.write("{t.yellow}{m.output}{t.normal}\n", m=m)

    def summary(self):
        total_seconds, by_code = self._calculate()
        if len(self.messages):
            self.write('\n')
        self.report_errors(by_code)
        for ec, ct in by_code.items():
            self.write("{}: {} ", self.status_flags.get(ec), ct)
        self.write("Total: {} ({} sec)\n",
                   len(self.messages), total_seconds)

    def exit(self):
        for m in self.messages:
            if m['returncode'] != 0:
                sys.exit(1)
        sys.exit(0)


class DotReporter(Reporter):
    responses = {
        0: '.',
        -1: 'E',
        1: 'E',
        None: 'F'
    }

    def emit(self, msg):
        super(DotReporter, self).emit(msg)
        ec = msg.get('returncode', 0)
        if self.options and self.options.verbose:
            log.info(msg['test'])
        self.write(self.responses.get(ec, 'F'))
        self.fp.flush()

    def header(self):
        self.write("Running Tests...\n")


class JSONReporter(Reporter):
    def summary(self):
        json.dump(self.messages, self.fp, indent=2)
        self.write('\n')
        self.fp.flush()
