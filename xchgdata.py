import queue
import io
import sys
import json
import requests
import urllib
import logging
import traceback
import time
from datetime import datetime

# TODO: разнести в осмысленные места
tasks_queue = queue.Queue()
commands_queue = queue.Queue()
errors_queue = queue.Queue()

# # logger = initialize_logging()
# def initialize_logging():
# # def initialize_logging(options):
#     """ Log information based upon users options"""

#     logger = logging.getLogger('master')
#     formatter = logging.Formatter('%(asctime)s %(levelname)s\t%(message)s')
#     # level = logging.__dict__.get(options.loglevel.upper(),logging.DEBUG)
#     level = logging.DEBUG
#     logger.setLevel(level)

#     # # Output logging information to screen
#     # if not options.quiet:
#     #     hdlr = logging.StreamHandler(sys.stderr)
#     #     hdlr.setFormatter(formatter)
#     #     logger.addHandler(hdlr)

#     # Output logging information to file
#     # logfile = os.path.join(options.logdir, "_master.log")
#     logfile = "_master.log"
#     # if options.clean and os.path.isfile(logfile):
#     #     os.remove(logfile)
#     hdlr2 = logging.FileHandler(logfile)
#     hdlr2.setFormatter(formatter)
#     logger.addHandler(hdlr2)

#     return logger


# https://stackoverflow.com/questions/616645/how-do-i-duplicate-sys-stdout-to-a-log-file-in-python/2216517#2216517
class LogFile:
    """File-like object to log text using the `logging` module."""

    def __init__(self, name=None):
        self.logger = logging.getLogger(name)

    def write(self, msg, level=logging.INFO):
        self.logger.log(level, msg)

    def flush(self):
        for handler in self.logger.handlers:
            handler.flush()


logging.basicConfig(level=logging.DEBUG, handlers=[logging.FileHandler('_master.log', 'w', 'utf-8')])
sys.stdout = LogFile('stdout')
sys.stderr = LogFile('stderr')


# logging.basicConfig(level=logging.DEBUG, filename='mylog.log')

# # Redirect stdout and stderr
# sys.stdout = LogFile('stdout')
# sys.stderr = LogFile('stderr')

# def main(argv=None):
#     if argv is None:
#         argv = sys.argv[1:]

#     # Setup command line options
#     parser = OptionParser("usage: %prog [options]")
#     parser.add_option("-l", "--logdir", dest="logdir", default=".", help="log DIRECTORY (default ./)")
#     parser.add_option("-v", "--loglevel", dest="loglevel", default="debug", help="logging level (debug, info, error)")
#     parser.add_option("-q", "--quiet", action="store_true", dest="quiet", help="do not log to console")
#     parser.add_option("-c", "--clean", dest="clean", action="store_true", default=False, help="remove old log file")

#     # Process command line options
#     (options, args) = parser.parse_args(argv)

#     # Setup logger format and output locations
#     logger = initialize_logging(options)

#     # Examples
#     logger.error("This is an error message.")
#     logger.info("This is an info message.")
#     logger.debug("This is a debug message.")

# class Tee(object):
#     def __init__(self, name, mode):
#         self.file = open(name, mode)
#         self.stdout = sys.stdout
#         sys.stdout = self

#     def __del__(self):
#         sys.stdout = self.stdout
#         self.file.close()

#     def write(self, data):
#         self.file.write(data)
#         self.stdout.write(data)

#     def flush(self):
#         self.file.flush()

#     def __enter__(self):
#         pass

#     def __exit__(self, _type, _value, _traceback):
#         pass


# @app.before_first_request
# def startup():
#     import os

#     with open('master-0.pid', 'w') as fpid:
#         pid = os.getpid()
#         fpid.write(str(pid))

#     print("Main thread [{}] started".format(pid))

#     with ThreadPoolExecutor(2) as executor:
#         executor.submit(worker, cfg, tasks_queue)

def worker(cfg, tasks_queue):
    """
    Takes tasks from queue and send them to slave(s)
    """
    import os

    pid = os.getpid()

    print("Worker [{}] is started".format(pid), flush=True)
    slave_config = cfg['slave']

    while True:
        if tasks_queue.empty():
            print("Очередь пуста...", flush=True)
            time.sleep(1)
            continue

        print("О, задание!", flush=True)
        print("Очередь до:", tasks_queue.qsize())
        task = tasks_queue.get()
        print("Очередь после:", tasks_queue.qsize())
        print("Получено!", flush=True)
        obj = {'json': 'data', 'test': task}

        # Здесь при ошибках могут теряться задания, если не предусмотреть что-либо
        # Съедаются исключения, если их не обрабатывать и не возвращать куда-то
        try:
            r = requests.post('http://{host}:{port}/perfang/api/slave/v0.1/run'.format(**slave_config), json=obj, )
            response = r.json()
            # time.sleep(0.1)
        except Exception as e:
            # https://stackoverflow.com/questions/33448329/how-to-detect-exceptions-in-concurrent-futures-in-python3
            # https://stackoverflow.com/questions/29177490/how-do-you-kill-futures-once-they-have-started
            # https://github.com/tornadoweb/tornado/issues/1595
            # https://stackoverflow.com/questions/27478602/how-to-use-a-thread-pool-to-do-infinite-loop-function
            # https://opensourcehacker.com/2017/01/30/simple-loop-parallelization-in-python/
            # http://qaru.site/questions/820759/how-to-use-a-thread-pool-to-do-infinite-loop-function
            exc_buffer = io.StringIO()
            traceback.print_exc(file=exc_buffer)
            print("Исключение", e)
            logging.error('Uncaught exception in worker process:\n%s', exc_buffer.getvalue())
            # errors_queue.put(e)
            errors_queue.put(exc_buffer.getvalue())
            # raise e
