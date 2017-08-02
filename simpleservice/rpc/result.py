from simpleutil.utils import timeutils

class BaseRpcResult(object):

    def __init__(self, ctxt=None, agent_id=0,
                 resultcode=0, result=None, details=None):
        self.agent_id = agent_id
        self.resultcode = resultcode
        self.result = result
        self.details = details
        self.agent_time = int(timeutils.realnow())
        self.persist = ctxt.get('persist', None)
        self.expire = ctxt.get('expire', None)


    def to_dict(self):
        ret_dict = {'resultcode': self.resultcode,
                    'result': self.result if self.result else 'unkonwn result',
                    'agent_time': self.agent_time}
        if self.agent_id:
            ret_dict['agent_id'] = self.agent_id
        if self.details:
            ret_dict['details'] = self.details
        if self.persist:
            ret_dict['persist'] = self.persist
        if self.expire:
            ret_dict['expire'] = self.expire
        return ret_dict



