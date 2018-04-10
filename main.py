import device

class MainApp(object):
    """ Application repsonsible for initalizing and running the shell. """

    __TITLE = "pyLunchbox"
    __VER_MAJOR = 0
    __VER_MINOR = 1
    __VER_LEVEL = 1
    __VERSION = "Version {:d}.{:d}.{:d}".format(__VER_MAJOR, __VER_MINOR, __VER_LEVEL)

    @classmethod
    def init(cls):
        """ Initialize the app. """

        device.init(cls, cls.get_full_title())

    @classmethod
    def main(cls):
        """ Main function to run the app. """

        pass

    @classmethod
    def get_version(cls):
        """ Get the version of this app. """

        return cls.__VERSION

    @classmethod
    def get_full_title(cls):

        return "{:s} {:s}".format(cls.__TITLE, cls.__VERSION)

    @classmethod
    def destroy(cls):
        """ Kill the app. """

        device.shutdown()

if __name__ == "__main__":

    MainApp.init()
    print MainApp.get_full_title()
    MainApp.destroy()
