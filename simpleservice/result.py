
class BaseResult(object):

    def __init__(self, resultcode=0, result=None, data=None):
        self.resultcode = resultcode
        self.result = result
        self.data = data

    def to_dict(self):
        return {'resultcode': self.resultcode,
                'result': self.result if self.result else 'unkonwn result',
                'data': self.data if self.data else []
                }
