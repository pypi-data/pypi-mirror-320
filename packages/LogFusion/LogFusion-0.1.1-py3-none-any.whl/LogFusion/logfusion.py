from LogFusion.logger import Logger
from LogFusion.reader import Reader
from LogFusion.runner import Runner
from LogFusion.spinner import Spinner
import threading

class LogFusion:
    def __init__(self):
        self.logger = Logger()
        self.spinner = Spinner()
        self.mutex = threading.Lock()
        self.output_reader = Reader(self.logger, self.spinner, self.mutex)
        self.command_runner = Runner(self.logger, self.output_reader, self.mutex)

    def start(self, commands):
        output_thread = threading.Thread(target=self.output_reader.read_output, daemon=True)
        output_thread.start()

        self.command_runner.run_commands(commands)

        for line in self.logger.get_messages():
            print(line)