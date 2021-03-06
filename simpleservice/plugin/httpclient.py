import eventlet
import requests
import six.moves.urllib.parse as urlparse

from requests.exceptions import ReadTimeout

from simpleutil.config import cfg
from simpleutil.utils import encodeutils
from simpleutil.utils import jsonutils
from simpleutil.log import log as logging

from simpleservice import common
from simpleservice.plugin import exceptions


CONF = cfg.CONF

LOG = logging.getLogger(__name__)


def results(total=0,
            pagenum=0,
            result=None,
            data=None,
            resultcode=common.RESULT_SUCCESS):
    ret_dict = {'resultcode': 0,
                'total': 0,
                'pagenum': 0,
                'result': 'unkonwn result',
                'data': []}
    if result:
        ret_dict['result'] = result
    if total:
        ret_dict['total'] = total
    if pagenum:
        ret_dict['pagenum'] = pagenum
    if resultcode:
        ret_dict['resultcode'] = resultcode
    if data:
        ret_dict['data'] = data
        if not ret_dict['total']:
            ret_dict['total'] = len(ret_dict['data'])
    if not isinstance(ret_dict['data'], list):
        raise TypeError('results data type error')
    return ret_dict


class HttpClientBase(object):
    """Client for the Http request.
    """
    USER_AGENT = 'simpleservice-httpclient'
    CONTENT_TYPE = 'application/json'
    FORMAT = 'json'

    TYPES = {'public': 'v', 'private': 'n'}

    def __init__(self, url, port=80, **kwargs):
        """Initialize a new client for the http request."""
        super(HttpClientBase, self).__init__()
        url = url.lower()
        if not url.startswith('http://'):
            self.url = 'http://%s' % url
        else:
            self.url = url
        if port != 80:
            self.url += ':%d' % port
        if self.url.endswith('/'):
            self.url = self.url[:-1]
        _type = kwargs.pop('type', 'private')
        _type = HttpClientBase.TYPES[_type]
        self.session = kwargs.pop('session', None)
        self.version = kwargs.pop('version', 'v1.0')
        self.retries = kwargs.pop('retries', 1)
        self.timeout = kwargs.pop('timeout', 5.0)
        self.token = kwargs.pop('token', None)
        self.raise_errors = kwargs.pop('raise_errors', True)
        self.retry_interval = 1

    def _do_request(self, action, method, headers, body, timeout):
        request_url = self.url + action
        if len(request_url) > common.MAX_URI_LEN:
            raise exceptions.BeforeRequestError('Error url, url len over then %d' % common.MAX_URI_LEN)
        if self.session:
            resp = self.session.request(method, request_url, headers=headers, data=body,
                                        timeout=timeout, allow_redirects=False)
        else:
            resp = requests.request(method, request_url, headers=headers, data=body,
                                    timeout=timeout, allow_redirects=False)
        return resp, resp.content

    def do_request(self, method, action,
                   body=None, headers=None, params=None,
                   timeout=None, version=None):
        # action += ".%s" % self.FORMAT
        timeout = timeout if timeout else self.timeout
        headers = headers or {}
        headers.setdefault('User-Agent', self.USER_AGENT)
        headers.setdefault('Content-Type', self.CONTENT_TYPE)
        headers.setdefault('Accept', self.CONTENT_TYPE)
        if self.token:
            headers.setdefault(common.TOKENNAME, self.token)
        action = '/%s%s' % (version or self.version, action)
        try:
            if isinstance(params, dict) and params:
                params = encodeutils.safe_encode_dict(params)
                action += '?' + urlparse.urlencode(params, doseq=1)
            if body:
                body = self.serialize(body)
        except Exception as e:
            raise exceptions.BeforeRequestError('Encode params or serialize catch %s' % e.__class__.__name__)
        try:
            resp, replybody = self._do_request(action, method, headers, body=body, timeout=timeout)
        except ReadTimeout as e:
            LOG.error('request timeout %s' % e.message)
            if LOG.isEnabledFor(logging.DEBUG):
                LOG.exception('timeout')
            raise
        except Exception as e:
            LOG.warning('%s %s%s fail, %s' % (method, self.url, action, e.__class__.__name__))
            raise exceptions.ConnectionFailed('Send request catch error')
        # 200: ('ok', 'okay', 'all_ok', 'all_okay', 'all_good',
        # 201: ('created',),
        # 202: ('accepted',),
        # 203: ('non_authoritative_info', 'non_authoritative_information'),
        # 204: ('no_content',),
        # 205: ('reset_content', 'reset'),
        # 206: ('partial_content', 'partial'),
        # 207: ('multi_status', 'multiple_status', 'multi_stati', 'multiple_stati'),
        # 208: ('already_reported',),
        status_code = resp.status_code
        if status_code in (requests.codes.ok,
                           requests.codes.created,
                           requests.codes.accepted,
                           requests.codes.no_content):
            data = self.deserialize(replybody, status_code)
            return resp, data
        else:
            if not replybody:
                replybody = resp.reason
            self._handle_fault_response(status_code, replybody, resp)

    def retry_request(self, method, action,
                      body=None, headers=None, params=None,
                      timeout=None, version=None):
        """Call do_request with the default retry configuration.

        Only idempotent requests should retry failed connection attempts.
        :raises: ConnectionFailed if the maximum # of retries is exceeded
        """
        timeout = timeout if timeout else self.timeout
        max_attempts = self.retries + 1
        for i in range(max_attempts):
            try:
                return self.do_request(method, action, body=body,
                                       headers=headers, params=params, timeout=timeout, version=version)
            except (exceptions.BeforeRequestError,
                    exceptions.ServerNotImplementedError,
                    exceptions.ClientRequestError):
                raise
            except exceptions.ConnectionFailed:
                # Exception has already been logged by do_request()
                if i < self.retries:
                    LOG.debug('Retrying connection to %s' % action)
                    eventlet.sleep(self.retry_interval)
                elif self.raise_errors:
                    raise

        if self.retries:
            msg = ("Failed to connect to http server after %d attempts" % max_attempts)
        else:
            msg = "Failed to connect http server"

        raise exceptions.ConnectionFailed(msg)

    def _handle_fault_response(self, status_code, response_body, resp):
        # Create exception with HTTP status code and message
        try:
            json_data = jsonutils.loads_as_bytes(response_body)
            resone = json_data.get('msg') if json_data.get('msg') else response_body
        except ValueError:
            resone = response_body
        except Exception:
            LOG.exception('Resopne error')
            raise
        if 400 <= status_code < 500:
            LOG.debug('Http request get client error: %s' % str(resone))
            raise exceptions.ClientRequestError(code=status_code, resone=resone)
        elif 500 <= status_code < 600:
            LOG.debug('Http request get server error: %s' % str(resone))
            if status_code == 501:
                raise exceptions.ServerNotImplementedError(resone=resone)
            raise exceptions.ServerInternalError(code=status_code, resone=resone)
        else:
            LOG.error('Http request unknown error: %s' % str(resone))
            raise exceptions.ServerRsopneCodeError(code=status_code, resone=resone)

    def serialize(self, data):
        """Serializes a dictionary into JSON.
        A dictionary with a single key can be passed and it can contain any
        structure.
        """
        if data is None:
            return None
        elif isinstance(data, dict):
            return jsonutils.dumps_as_bytes(data)
        else:
            raise Exception("Unable to serialize object of type = '%s'" % type(data))

    def deserialize(self, data, status_code):
        """Deserializes a JSON string into a dictionary.
        return: type dict, data make by function `results` above this class
        """
        if status_code == 204:
            return data
        return jsonutils.loads_as_bytes(data)

    def delete(self, action, body=None, headers=None, params=None,
               timeout=None, version=None):
        return self.retry_request("DELETE", action, body=body,
                                  headers=headers, params=params,
                                  timeout=timeout, version=version)

    def get(self, action, body=None, headers=None, params=None,
            timeout=None, version=None):
        return self.retry_request("GET", action, body=body,
                                  headers=headers, params=params,
                                  timeout=timeout, version=version)

    def post(self, action, body=None, headers=None, params=None,
             timeout=None, version=None):
        # Do not retry POST requests to avoid the orphan objects problem.
        return self.do_request("POST", action, body=body,
                               headers=headers, params=params,
                               timeout=timeout, version=version)

    def retryable_post(self, action, body=None, headers=None, params=None,
                       timeout=None, version=None):
        return self.retry_request("POST", action, body=body,
                                  headers=headers, params=params,
                                  timeout=timeout, version=version)

    def put(self, action, body=None, headers=None, params=None,
            timeout=None, version=None):
        return self.retry_request("PUT", action, body=body,
                                  headers=headers, params=params,
                                  timeout=timeout, version=version)

    def head(self, action, body=None, headers=None, params=None,
             timeout=None, version=None):
        return self.retry_request("HEAD", action, body=body,
                                  headers=headers, params=params,
                                  timeout=timeout, version=version)

    def patch(self, action, body=None, headers=None, params=None,
              timeout=None, version=None):
        # Do not retry PATCH requests to avoid the orphan objects problem.
        return self.do_request("PATCH", action, body=body,
                               headers=headers, params=params,
                               timeout=timeout, version=version)

    def retryable_patch(self, action, body=None, headers=None, params=None,
                        timeout=None, version=None):
        return self.retry_request("PATCH", action, body=body,
                                  headers=headers, params=params,
                                  timeout=timeout, version=version)

    def options(self, action, body=None, headers=None, params=None,
                timeout=None, version=None):
        return self.retry_request("OPTIONS", action, body=body,
                                  headers=headers, params=params,
                                  timeout=timeout, version=version)
