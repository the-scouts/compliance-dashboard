import multiprocessing

bind = "0.0.0.0"
timeout = 600
loglevel = "debug"
workers = multiprocessing.cpu_count() * 2 + 1
