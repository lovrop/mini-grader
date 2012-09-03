import time

from .clint.textui import colored
from .runner import Runner

class Scoreboard:
    '''Monitors the results of individual test cases and display their status.'''

    def __init__(self):
        self.monitors = []
        self.first_column_width = 0
    
    def add(self, infile, runner, future):
        self.monitors.append(SingleRunMonitor(infile, runner, future, self.write_row))
        self.first_column_width = max(self.first_column_width, len(infile))

    def start(self):
        while self.monitors:
            self.monitors.pop(0).run()
            print()

    def write_row(self, infile, runner):
        time = runner.get_time()
        memory = int(runner.get_memory() / 1048576)

        memstr = ''
        if memory:
            memstr = '%4dM' % memory
                     
        print('\r%-*s | %s | %5.2f | %5s' %
              (self.first_column_width,
               infile,
               self.get_text_status(13, runner),
               time,
               memstr),
              end='')

    def get_text_status(self, width, runner):
        color, text = self._get_text_color_and_status(runner)
        text = '%-*s' % (width, text)
        return color(text) if color is not None else text

    def _get_text_color_and_status(self, runner):
        status_to_color_text = {
            Runner.WAITING:  (None, 'Waiting'),
            Runner.RUNNING:  (None, 'Running'),
            Runner.CHECKING: (None, 'Checking'),
            }
        if runner.status in status_to_color_text:
            return status_to_color_text[runner.status]
        assert runner.status == Runner.DONE
        
        result_to_color_text = {
            Runner.Result.PASSED:        (colored.green, 'Passed'),
            Runner.Result.WRONG_ANSWER:  (colored.red, 'Wrong answer'),
            Runner.Result.TIME_LIMIT:    (colored.yellow, 'Time limit'),
            Runner.Result.MEMORY_LIMIT:  (colored.cyan, 'Memory limit'),
            Runner.Result.RUNTIME_ERROR: (colored.magenta, 'Runtime error'),
            }
        return result_to_color_text[runner.result]

    
class SingleRunMonitor:
    def __init__(self, infile, runner, future, write_row_callback):
        self.infile = infile
        self.runner = runner
        self.future = future
        self.write_row_callback = write_row_callback

    def update(self):
        self.write_row_callback(self.infile, self.runner)
        
    def run(self):
        while not self.future.done():
            self.update()
            time.sleep(0.1)
        self.update()
        if self.future.exception() is not None:
            raise self.future.exception()
