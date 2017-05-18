import webob.exc
from sqlalchemy import func

from simpleutil.common.exceptions import InvalidArgument

from simpleutil.utils.argutils import Idformater
from simpleutil.utils.argutils import IdformaterBase

from simpleservice.plugin.manager import get_session
from simpleservice.plugin.manager.models import WsgiRequest
from simpleservice.ormdb.api import model_query

FAULT_MAP = {InvalidArgument: webob.exc.HTTPClientError}


class AsyncWorkRequest(IdformaterBase):

    def __init__(self):
        IdformaterBase.__init__(self)


    def index(self, req, body):
        max_rows = 100
        session = get_session(readonly=True)
        query = model_query(session, WsgiRequest)
        rows_num = query(func.count("*")).select_from(WsgiRequest).scalar()
        if rows_num >= max_rows:
            query = query.limit(100)
        page_num = int(body.get('page', 0))
        if page_num*10 >= rows_num:
            raise InvalidArgument('Page number over size')
        # index in request_time
        # so first filter is request_time
        start_time = int(body.get('start_time', 0))
        end_time = int(body.get('start_time', 0))
        if start_time:
            query = query.filter(WsgiRequest.request_time>=start_time)
        if end_time:
            query = query.filter(WsgiRequest.request_time<end_time)
        sync = body.get('sync', True)
        async = body.get('async', True)
        if not sync and async:
            raise InvalidArgument('No both sync and async mark')
        if sync and not async:
            query.filter(WsgiRequest.async_checker==0)
        elif async and not sync:
            query = query.filter(WsgiRequest.async_checker!=0)
        if page_num:
            query.seek(page_num*10)
        ret_list = {'total':rows_num, 'data':[], 'msg':'Get request list success'}
        for result in  query:
            data = dict(request_id=result.request_id,
                        status=result.status,
                        request_time=result.request_time,
                        async_checker=result.async_checker,
                        result=result.result,
                        )
            ret_list['data'].append(data)
        return ret_list



    @Idformater(key='request_id', all_key=None)
    def show(self, req, request_id, body):
        session = get_session(readonly=True)
        query = model_query(session, WsgiRequest)
        row = query.filter_by(request_id=request_id).first()
        agent_resopne = row.respones

