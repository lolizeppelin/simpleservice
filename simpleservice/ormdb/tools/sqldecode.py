# -*- coding: utf-8 -*-
"""
sql文件解析工具,用于将sql文件解析为单条sql语句
"""
import re

CHUNKSIZE = 4096


class MysqlAnalyze(object):
    """
    mysql文本语法解析工具
    """
    # 注释
    COMMENTS = {'-': ('--', '\n'),
                '/': ('/*', '*/')}
    # 空头
    EMPTYSTART = ('\n', '\t', ' ', '\r')
    # 默认结束符
    DEFAULTDELIMITER = ';'
    # DELIMITER语句
    DELIMITERSQL = 'DELIMITER'
    DELIMITERMARK = re.compile('^DELIMITER\s+?(\S+?)\s*?\n$', re.IGNORECASE)

    QUOTATIONS = frozenset(["'", '"', '`'])

    # ----------------下面为格式化正则--------------------

    # 禁止语句匹配
    REFUSE = re.compile('(^(CREATE|DROP)\s+?DATABASE\s|^USE\s).+?$', re.IGNORECASE | re.DOTALL)

    # ----------------TABLE--------------------
    TABLES = re.compile('(^(CREATE|DROP|ALTER)\s+?TABLE\s|'
                        '^(TRUNCATE)\s[\s*?TABLE\s]{0,1}|'
                        '^(INSERT|REPLACE)\s+?INTO\s|'
                        '^(UPDATE)\s+?SET\s|'
                        '^(DELETE)\s+?FROM\s).+?$', re.IGNORECASE | re.DOTALL)
    # 匹配create table中auto increment
    AUTOINCREMENT = re.compile('AUTO_INCREMENT=\d+?\s', re.IGNORECASE)
    # 匹配create table中partition语句
    PARTIONS = re.compile('/\*\!50100\s+?(PARTITION\s+BY\s+[\S\s]+?)\*/', re.IGNORECASE | re.DOTALL)

    # ----------------PROC/VEIW/FUNCTION/TARGGER--------------------
    CVIEWS = re.compile('/\*\!50001\s+(CREATE\s+VIEW\s+.+?)*\s*?\*/$', re.IGNORECASE | re.DOTALL)
    DROPS = re.compile('/\*\!50003\s+?(DROP\s+?(PROCEDURE|FUNCTION|TRIGGER|VIEW)\s.+?)*\s*?\*/$',
                       re.IGNORECASE | re.DOTALL)  # 注释中的DROP语句
    # 匹配DEFINER,用于删除
    DEFINERPATTERN = re.compile('^(CREATE|DROP)\s+?'
                                '(ALGORITHM=.+?\s+?){0,1}'
                                '(DEFINER=.+?\s+?){0,1}'
                                '(SQL\s+?SECURITY\s+?DEFINER\s+?){0,1}'
                                '(PROCEDURE|FUNCTION|TRIGGER|VIEW)', re.IGNORECASE | re.DOTALL)

    def __init__(self, path):
        self.path = path
        self.finished = False
        # 当前结束符
        self.delimiter = MysqlAnalyze.DEFAULTDELIMITER
        # 单独结束符
        self.single_delimiter = re.compile('^\s*?%s\s*?\n' % self.delimiter)
        # 快引用
        self.block_quotations = None
        # 当前行
        self.line = 0

        self.results = {
            'TABLE': {
                'DROP': [],
                'TRUNCATE': [],
                'CREATE': [],
                'ALTER': [],
                'INSERT': [],
                'REPLACE': [],
                'UPDATE': [],
                'DELETE': [],
            },
            'PROCEDURE': {'CREATE': [], 'DROP': []},
            'FUNCTION': {'CREATE': [], 'DROP': []},
            'TRIGGER': {'CREATE': [], 'DROP': []},
            'VIEW': {'CREATE': [], 'DROP': []}
        }

    @property
    def result(self):
        return self.results

    def printing(self):
        for target in self.results:
            print '-------------%s----------------' % target
            for action in self.results[target]:
                for sql in self.results[target][action]:
                    print sql
                    print '--------------------------------'

    def analyze(self, raw):
        if raw[-len(self.delimiter):] == self.delimiter:  # 遇到结束符,解析sql语句
            # 去除结尾的结束符
            sql = raw[:-len(self.delimiter)]
            if not sql:  # 单独结束符
                return True
            if re.match(self.REFUSE, sql):
                raise ValueError('Not allow sql of %s' % sql)
            match = re.match(self.TABLES, sql)
            if match:
                target = 'TABLE'
                for action in match.groups()[1:]:
                    if action:
                        break
                if action == 'CREATE':
                    # 去除自增长
                    sql = re.sub(self.AUTOINCREMENT, '', sql)
                    partions = re.findall(self.PARTIONS, sql)
                    # 去除partion语句的注释
                    for partion in partions:
                        sql = sql.replace(partion[0], partion[1], 1)
                self.results[target][action].append(sql)
                return True
            match = re.match(self.DEFINERPATTERN, sql)
            if match:
                action = match.group(1)
                target = match.group(5)
                self.results[target][action].append(sql.replace(match.group(), '%s %s' % (action, target)))
                return True
            raise ValueError('Sql not match, %s' % raw)
        if re.match(self.single_delimiter, raw):  # 单独结束符
            return True
        return False

    def in_quotations(self, buf):
        # 在引用块中
        if self.block_quotations is not None:
            quote_mark = self.block_quotations[-1]
            if buf[-1] == quote_mark and buf[-2] != '\\':  # block_quotations不为空buf肯定>=2
                self.block_quotations = None
        elif buf[-1] != self.delimiter and buf[-1] in self.QUOTATIONS:
            if len(buf) >= 2 and buf[-2] == '\\':  # 连续转义符号直接报错
                raise ValueError('Block Quotations error, line %d' % (self.line + 1))
            self.block_quotations = buf[-1]
        return self.block_quotations is not None

    def is_delimiter(self, buf):
        r = re.match(self.DELIMITERMARK, buf)
        if r:
            # 更改结束符
            self.delimiter = r.group(1)
            # 单独结束符 正则变更
            self.single_delimiter = re.compile('^\s*?%s\s*?\n' % self.delimiter)
            return True
        return False

    def __call__(self):
        # 语句堆
        heap = ''

        # 堆是注释
        comments_heap = False
        # 注释开头匹配
        comments_match = False

        # 堆是sql
        sql_heap = False
        # 可能是delimiter语句
        maybe_delimiter = False

        if self.finished:
            return self.result
        with open(self.path, 'r') as f:
            while True:
                raw = f.read(CHUNKSIZE)
                if not raw:
                    break
                for s in raw:
                    # 行计数器
                    if s == '\n':
                        self.line += 1
                    if not comments_heap and not sql_heap:
                        if s in self.EMPTYSTART:  # 为空字符串
                            continue
                        if s in self.COMMENTS:
                            comments_heap = True
                        else:
                            sql_heap = True
                    heap += s
                    if comments_heap:  # 在注释中
                        start, end = self.COMMENTS[heap[0]]
                        if not comments_match:  # 注释头未匹配
                            if len(heap) >= len(start):
                                if heap[:len(start)] != start:
                                    raise ValueError('Comments prefix not match, line %d' % (self.line + 1))
                                comments_match = True
                        elif len(heap) >= len(end):
                            if heap[-len(end):] == end:
                                if start == self.COMMENTS['/'][0]:
                                    match = re.match(self.CVIEWS, heap)
                                    if match:
                                        action = 'CREATE'
                                        target = 'VIEW'
                                        sql = match.group(1)
                                        self.results[target][action].append(sql)
                                    else:
                                        match = re.match(self.DROPS, heap)
                                        if match:
                                            action = 'DROP'
                                            target = match.group(2)
                                            sql = match.group(1)
                                            self.results[target][action].append(sql)
                                heap = ''
                                comments_heap = False
                                comments_match = False
                    elif sql_heap:  # 在sql语句中
                        if self.in_quotations(heap):  # 在引用块中
                            continue
                        if maybe_delimiter:  # 有可能是 delimiter语句
                            if len(heap) <= len(self.DELIMITERSQL):
                                if heap.upper() != self.DELIMITERSQL[:len(heap)]:
                                    # 不以DELIMITER字符串开头,确定不是DELIMITER语句
                                    maybe_delimiter = False
                            # sql语句大于DELIMITER语句最小长长度DELIMITER ;\n
                            elif len(heap) >= len(self.DELIMITERSQL) + 3:
                                if self.is_delimiter(heap):  # 确定是DELIMITER语句
                                    heap = ''
                                    sql_heap = False
                                    maybe_delimiter = True
                        elif len(heap) >= len(self.delimiter):  # 语句长度足够结束
                            if self.analyze(heap):  # 解析sql语句成功并置空语句堆
                                sql_heap = False
                                maybe_delimiter = True
                                heap = ''
            self.finished = True
        return self.result


def analyze(sqlfile, drop_table=False, with_data=False):
    pass
