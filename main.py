
class General:

    def __init__(self, id, state='NF'):
        self.id = id
        self.state = state
        self.received_orders = {}
        self.decision = None


