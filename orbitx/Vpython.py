import vpython
import signal

vpython_object = vpython
container = [vpython_object]
closed = False

def vpython_version_check() -> None :
    print("version check is executed")
    ctrl_c_handler: function = signal.getsignal(signal.SIGINT)
    if vpython_object.__version__ == '7.4.7':
        # vpython installs "os._exit(0)" signal handlers in 7.4.7.
        # Very not good for us.
        # Reset the signal handler to default behaviour.
        signal.signal(signal.SIGINT, ctrl_c_handler)

        # os._exit(0) is in one other place, let's take that out too.
        # Unfortunately, now that vpython isn't calling os._exit, we have
        # to notify someone when the GUI closed.
        # Note to access vpython double underscore variables, we have to
        # bypass normal name mangling by using getattr.
        def callback(*_):
            getattr(vpython_object.no_notebook, '__interact_loop').stop()
            closed = True
        # end of callback
        getattr(vpython_object.no_notebook,'__factory').protocol.onClose = callback
# end of _vpython_version_check

def vp() -> vpython:
    return container[0]

