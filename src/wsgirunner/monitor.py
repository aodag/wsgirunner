import sys
import os
import time
import threading

class classinstancemethod(object):
    """
    Acts like a class method when called from a class, like an
    instance method when called by an instance.  The method should
    take two arguments, 'self' and 'cls'; one of these will be None
    depending on how the method was called.
    """

    def __init__(self, func):
        self.func = func
        self.__doc__ = func.__doc__

    def __get__(self, obj, type=None):
        return _methodwrapper(self.func, obj=obj, type=type)

class _methodwrapper(object):

    def __init__(self, func, obj, type):
        self.func = func
        self.obj = obj
        self.type = type

    def __call__(self, *args, **kw):
        assert not 'self' in kw and not 'cls' in kw, (
            "You cannot use 'self' or 'cls' arguments to a "
            "classinstancemethod")
        return self.func(*((self.obj, self.type) + args), **kw)

class Monitor(object): # pragma: no cover
    """
    A file monitor and server restarter.

    Use this like:

    ..code-block:: Python

        install_reloader()

    Then make sure your server is installed with a shell script like::

        err=3
        while test "$err" -eq 3 ; do
            python server.py
            err="$?"
        done

    or is run from this .bat file (if you use Windows)::

        @echo off
        :repeat
            python server.py
        if %errorlevel% == 3 goto repeat

    or run a monitoring process in Python (``pserve --reload`` does
    this).  

    Use the ``watch_file(filename)`` function to cause a reload/restart for
    other other non-Python files (e.g., configuration files).  If you have
    a dynamic set of files that grows over time you can use something like::

        def watch_config_files():
            return CONFIG_FILE_CACHE.keys()
        add_file_callback(watch_config_files)

    Then every time the reloader polls files it will call
    ``watch_config_files`` and check all the filenames it returns.
    """
    instances = []
    global_extra_files = []
    global_file_callbacks = []

    def __init__(self, poll_interval):
        self.module_mtimes = {}
        self.keep_running = True
        self.poll_interval = poll_interval
        self.extra_files = list(self.global_extra_files)
        self.instances.append(self)
        self.file_callbacks = list(self.global_file_callbacks)

    def _exit(self):
        # use os._exit() here and not sys.exit() since within a
        # thread sys.exit() just closes the given thread and
        # won't kill the process; note os._exit does not call
        # any atexit callbacks, nor does it do finally blocks,
        # flush open files, etc.  In otherwords, it is rude.
        os._exit(3)

    def periodic_reload(self):
        while True:
            if not self.check_reload():
                self._exit()
                break
            time.sleep(self.poll_interval)

    def check_reload(self):
        filenames = list(self.extra_files)
        for file_callback in self.file_callbacks:
            try:
                filenames.extend(file_callback())
            except:
                print(
                    "Error calling reloader callback %r:" % file_callback)
                traceback.print_exc()
        for module in sys.modules.values():
            try:
                filename = module.__file__
            except (AttributeError, ImportError):
                continue
            if filename is not None:
                filenames.append(filename)
        for filename in filenames:
            try:
                stat = os.stat(filename)
                if stat:
                    mtime = stat.st_mtime
                else:
                    mtime = 0
            except (OSError, IOError):
                continue
            if filename.endswith('.pyc') and os.path.exists(filename[:-1]):
                mtime = max(os.stat(filename[:-1]).st_mtime, mtime)
            if not filename in self.module_mtimes:
                self.module_mtimes[filename] = mtime
            elif self.module_mtimes[filename] < mtime:
                print("%s changed; reloading..." % filename)
                return False
        return True

    def watch_file(self, cls, filename):
        """Watch the named file for changes"""
        filename = os.path.abspath(filename)
        if self is None:
            for instance in cls.instances:
                instance.watch_file(filename)
            cls.global_extra_files.append(filename)
        else:
            self.extra_files.append(filename)

    watch_file = classinstancemethod(watch_file)

    def add_file_callback(self, cls, callback):
        """Add a callback -- a function that takes no parameters -- that will
        return a list of filenames to watch for changes."""
        if self is None:
            for instance in cls.instances:
                instance.add_file_callback(callback)
            cls.global_file_callbacks.append(callback)
        else:
            self.file_callbacks.append(callback)

    add_file_callback = classinstancemethod(add_file_callback)

def install_monitor(poll_interval=1, extra_files=None):

    mon = Monitor(poll_interval=poll_interval)
    if extra_files is None:
        extra_files = []
    mon.extra_files.extend(extra_files)
    t = threading.Thread(target=mon.periodic_reload)
    t.setDaemon(True)
    t.start()
