class Browser:
    """docstring for Browser"""
    def __init__(self, arg):
        # super(Browser, self).__init__()
        # 
        # У браузеров есть окна и табы
        self.arg = arg

    def _start(self):
        """
        Запускает браузер.
        Делать ли этот метод приватным?
        """
        pass

    def stop(self):
        pass

    # Нужен деструктор, закрывающий браузер,
    # на случай удаления объекта

    # https://stackoverflow.com/questions/865115/how-do-i-correctly-clean-up-a-python-object

    # И использовать __enter__/__exit__
    # для работы с with


class Windows:
    """Browser Window class"""
    pass


class Tab:
    """Tab class"""
    pass


class Chrome(Browser):
    """Chrome Browser class"""
    pass


class Firefox(Browser):
    """Firefox browser class"""
    pass


class FakeBrowser(Browser):
    """Fake browser for testing purposes"""
    pass


# https://en.wikipedia.org/wiki/Metaclass
