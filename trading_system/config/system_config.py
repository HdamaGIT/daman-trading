class SystemConfig:
    def __init__(self, mode='development'):
        self.mode = mode

    def is_live(self):
        return self.mode == 'live'

    def is_development(self):
        return self.mode == 'development'
