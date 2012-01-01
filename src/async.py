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
        'For each iteration of the main loop, take some work from the queue.'
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
                
def run(function, arguments, callback, data=None):
    '''Entry point for asynchronous method invocations. The callback
    signature should take the same arguments as the target function, and
    additionally take the optional 'data' parameter.'''
    queue.put((function, arguments, callback, data))
    
    if not thread.is_alive():
        thread.start()
    