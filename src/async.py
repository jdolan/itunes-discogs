from Queue import Empty, Queue
import gtk
import threading

gtk.threads_init()

class Thread(threading.Thread):
    'The worker thread enabling asynchronous method invocations.'
    def __init__(self):
        super(Thread, self).__init__()
        self.shutdown = False
        
    def run(self):
        while not self.shutdown:
            try:
                (function, arguments, callback, data) = queue.get(True, 0.01)
            except Empty:
                continue
            function(*arguments)
            cb_arguments = list(arguments)
            cb_arguments.append(data)
            gtk.idle_add(callback, *cb_arguments)

queue, thread = Queue(), Thread()
                
def run(function, arguments, callback, data):
    '''Entry point for asynchronous method invocations. The callback
    signature should take the same arguments as the target function, and
    additionally take the optional 'data' parameter.'''
    queue.put((function, arguments, callback, data))
    
    if not thread.is_alive():
        thread.start()
    
def abort():
    'Flush the queue of any pending method invocations.'
    while not queue.empty():
        queue.get()
        
def shutdown():
    'Stop the thread, waiting for it to terminate cleanly.'
    if thread.is_alive():
        thread.shutdown = True
        thread.join()
    