class SingleMetric:
    """docstring for SingleMetric"""
    def __init__(self, arg):
        self.arg = arg
        # source :: description
        # destination :: description
        # storage :: description (put, get, select, ...)
        # 
        # get
        # put
        # (получить при запросе ноды с ожиданием;
        # отправить запрос на получение; нода пришлёт
        # после окончания выполнения задания)

    def get(self, data):
        """
        """
        pass
        
    def put(self, data):
        """
        """
        pass


class Metrics:
    """
    Назавния методов нехороши
    Они должны получать либо отправлять запросы
    на получение метрик
    """
    def __init__(self, arg):
        super(Metric, self).__init__()
        self.arg = arg

    def get(self, data):
        pass

    def put(self, data):
        pass


class GeneralMetrics:
    """docstring for GeneralMetrics"""
    def __init__(self, arg):
        super(GeneralMetrics, self).__init__()
        self.storage = storage

