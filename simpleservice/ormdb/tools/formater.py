# -*- coding: utf-8 -*-
# 直接抄两年前的代码, 质量较差凑合用
import os
import re
from codecs import BOM_UTF8 as BOM_HEAD
from simpleutil.common.exceptions import InvalidArgument

# 注释正则
annotation_regx = re.compile('/\*.*?\*/', re.S)
# 表分区语句正则
partion_in_annotations = re.compile('(/\*\!50100\s+(PARTITION\s+BY\s+[\S\s]+?)\*/ {0,1});{0,1}', re.IGNORECASE)
# create Temporary view 语句正则
create_temporary_view_in_annotations = \
    re.compile('(/\*\!50001\s+(CREATE\s+VIEW\s+[\S\s]+?)(1\s+?AS\s+?`\S+?`){0,1}(\s*?,){0,1}\s*?\*/\s{0,1};{0,1})',
               re.IGNORECASE)
# drop 和 view 开头的语句
drop_and_view_in_annotations = \
    re.compile('(drop.+?(\*/){0,1};)|(VIEW\s+?[\S]+?\s+?as\s+?select[\s\S]+?(\*/){0,1};)', re.IGNORECASE)

# 包含在以DELIMITER开头DELIMITER结尾的部分
delimiter_and_annotations = re.compile('(DELIMITER[\s\S]+?DELIMITER\s+?;)|(/\*[\s\S]+?\*/ {0,1};{0,1})',
                                       re.IGNORECASE)
# create语句正则
create_regx = re.compile('(/\*!\d{1,10}\s+){0,1}create\s+?(DEFINER=\S+ ){0,1}\s*', re.IGNORECASE)

# DELIMITER结束标记  group(2) 表示存在DELIMITER后没有定义分割符就换行
delimiter_end_mark_regx = re.compile('(DELIMITER\s+?;\s*)|(DELIMITER\s*)', re.IGNORECASE)
# 常见的4中 DELIMITER重定义结束符
delimiter_end_regx_1 = re.compile('(end (\*/){0,1}\s*\$\$)|(end\s*$)|(\$\$)', re.IGNORECASE)
delimiter_end_regx_2 = re.compile('(end (\*/){0,1}\s*\;;)|(end\s*$)|(;;)', re.IGNORECASE)
delimiter_end_regx_3 = re.compile('(end (\*/){0,1}\s*!!)|(end\s*$)|(!!)', re.IGNORECASE)
delimiter_end_regx_4 = re.compile('(end (\*/){0,1}\s*!!)|(end\s*$)|(//)', re.IGNORECASE)

create_table_regx = re.compile('CREATE\s+(TABLE|VIEW)\s+?(([\s\S]*?)CREATE\s+(TABLE|VIEW)){0,}[\s\S]+?;\s*$',
                               re.IGNORECASE)
alter_table_regx = re.compile('ALTER\s+TABLE\s+.+?;\s*$', re.IGNORECASE)
replace_and_insert_regx = re.compile('(INSERT|REPLACE)\s+INTO\s+.+?;\s*$', re.IGNORECASE)
drop_incolum_regx = re.compile('DROP\s+(COLUMN|PRIMARY|KEY|INDEX)\s+.*', re.IGNORECASE)

_split_re = '(^CREATE DATABASE.+)|(^use .+?;\s*$)|' + \
            '(^insert into .+?;\s*$)|(^update .+?set .+?;\s*$)|(^alter\s+table\s+.+?;\s*$)|' + \
            '(^delete from .+?where .+?;\s*$)|(^truncate\s+[table]{0,1}.+?;\s*$)|' + \
            '(CREATE\s+?(DEFINER=.+?\s+?){0,1}(PROCEDURE|FUNCTION|TRIGGER){1}.*)|' + \
            '(DEFINER=.+?\s)|(^drop table.+?;\s*$)|(^drop\s+?database\s+?.+?;\s*$)|(drop\s{1}.+?;\s*$)|(.+?;\s*$)'
split_regx = re.compile(_split_re, re.IGNORECASE)
auto_increment_regx = re.compile('AUTO_INCREMENT=\d{1,20} {1}', re.IGNORECASE)
view_regx = re.compile('create\s+?(ALGORITHM=.+?\s+?){0,1}(DEFINER=.+?\s+?){0,1}(SQL\s+?SECURITY\s+?DEFINER\s+?)view',
                       re.IGNORECASE)

MAX_SQL_FILE_SIZE = 65535


def analyze(sqlfile, drop_table=False, with_data=False):
    """
    格式化mysqldump导出的sql文件
    @param sqlfile:   sql文件地址
    @param drop_table:      是否执行drop table命令
    @param with_data:       是否输出对数据有操作的语句
    @raise InvalidArgument: 参数错误
    @return: 可以直接被python exec的sql语句组成的列表
    """
    if drop_table not in (True, False):
        raise InvalidArgument('drop_table value error')
    if not os.path.exists(sqlfile) or not os.path.isfile(sqlfile):
        raise InvalidArgument('sqlfile can not be found or not a file')
    size = os.path.getsize(sqlfile)
    if size >= MAX_SQL_FILE_SIZE:
        raise InvalidArgument('size of sqlfile too large')

    # drop table的语句列表
    drop_table_list = []
    # 其他drop语句(存储过程,函数,触发器等
    other_drop_list = []
    # 创建语句列表
    create_list = []
    # 包含在delimiter中的sql语句
    sql_delimiter_list = []
    # 创建view语句
    view_sql_list = []
    # alter 语句
    alter_list = []
    # insert 语句
    insert_list = []
    # update 语句
    update_list = []
    # delete 语句
    delete_list = []
    # truncate 语句
    truncate_list = []
    with open(sqlfile, 'r') as f:
        lines = f.readlines()

    # 跳过注释的行
    checked_line_list = []
    for line in lines:
        # 标准sql结束符为单独一行直接报错,其实可以处理一下 直接塞到前一行的结尾
        # 但是还要对前一行内容做校验 太麻烦
        if line.strip() == ';':
            raise ValueError('first string is [;],error sql file')
        if len(line) >= 2:
            if line.startswith('--'):
                continue
            if line.lower().startswith('set'):
                continue
        checked_line_list.append(line)
    temp_string = ''.join(checked_line_list)
    # 去除BOMB头
    if temp_string[:3] == BOM_HEAD:
        temp_string = temp_string[3:]
    # 去除掉windows的\r换行符
    temp_string = temp_string.replace('\r', '')
    temp_string = re.sub(annotation_regx, '', temp_string)
    if len(temp_string) < 10:
        raise ValueError('query string less then 10')
    partion_string_list = re.findall(partion_in_annotations, temp_string)
    create_temporary_view_list = re.findall(create_temporary_view_in_annotations, temp_string)
    # 去除partion语句的注释
    for find_string in partion_string_list:
        temp_string = temp_string.replace(find_string[0], find_string[1], 1)
    # 去除所有create temporary view
    for find_string in create_temporary_view_list:
        temp_string = temp_string.replace(find_string[0], '', 1)
    # 获取在DELIMITER与注释中的字符串
    delimiter_and_annotations_res = re.findall(delimiter_and_annotations, temp_string)
    delimiter_start = 0
    # 结束正则
    delimiter_end_regx = None
    temp_list = []
    if len(delimiter_and_annotations_res) > 0:
        for res_tuple in delimiter_and_annotations_res:
            delimiter = res_tuple[0]
            annotations = res_tuple[1]
            if delimiter != '':  # DELIMITER字符串
                delimiter_list = delimiter.split('\n')
                for line in delimiter_list:
                    if line.strip() == '':
                        continue
                    if not delimiter_start:
                        # delimiter开始标记
                        delimiter_start = 1
                        delimiter_mark = re.sub('delimiter', '', line, flags=re.IGNORECASE).strip()
                        if delimiter_mark == '$$':
                            delimiter_end_regx = delimiter_end_regx_1
                        elif delimiter_mark == ';;':
                            delimiter_end_regx = delimiter_end_regx_2
                        elif delimiter_mark == '!!':
                            delimiter_end_regx = delimiter_end_regx_3
                        elif delimiter_mark == '//':
                            delimiter_end_regx = delimiter_end_regx_4
                        else:
                            raise ValueError('unknown delimiter_mark')
                        continue
                    else:
                        delimiter_end = re.search(delimiter_end_mark_regx, line)
                        if delimiter_end is not None:
                            # delimiter结束
                            delimiter_start = 0
                            if delimiter_end.group(1) is None:
                                raise ValueError('find a delimiter with out start or end mark')
                            delimiter_end_regx = None
                            continue
                    search_res = re.search(create_regx, line)
                    if search_res is not None:
                        temp_list.append('CREATE %s' % re.sub(create_regx, '', line))
                        continue
                    if delimiter_end_regx is not None:
                        end_res = re.search(delimiter_end_mark_regx, line)
                        if end_res is not None:
                            # end字符单独一行
                            if end_res.group(3) is not None:
                                raise ValueError('find key word end in one line')
                            # 其他行commit_mark字符串
                            if end_res.group(4) is not None:
                                raise ValueError('find commit_mark line')
                            # 修改存储过程结尾
                            temp_list.append('END')
                            sql_string = '\n'.join(temp_list)
                            temp_list = []
                            sql_delimiter_list.append(sql_string)
                            continue
                    temp_list.append(line)
            if annotations != '':  # 注释字符串
                # mysql 5.1的dump语句会把DROP PROCEDURE放注释中
                # 获取在注释中的drop语句
                drop_and_view_in_annotations_res = re.search(drop_and_view_in_annotations, annotations)
                if drop_and_view_in_annotations_res is not None:
                    drop_in_annotations_string = drop_and_view_in_annotations_res.group(1)
                    drop_ex_string = drop_and_view_in_annotations_res.group(2)
                    view_string = drop_and_view_in_annotations_res.group(3)
                    view_ex_string = drop_and_view_in_annotations_res.group(4)
                    # drop语句
                    if drop_in_annotations_string is not None:
                        if drop_ex_string is not None:
                            drop_in_annotations_string = drop_in_annotations_string.replace(drop_ex_string, '')
                        other_drop_list.append(drop_in_annotations_string)
                    # view语句
                    if view_string is not None:
                        if view_ex_string is not None:
                            view_string = view_string.replace(view_ex_string, '')
                        view_sql_list.append('CREATE %s' % view_string)
    # 还在匹配到delimiter开始的部分,说明没有匹配到delimiter结束符
    if delimiter_start:
        raise ValueError('delimiter not end')
    # 获取去除注释和delimiter的部分
    no_annotations_string = re.sub(delimiter_and_annotations, '', temp_string)
    # 分行校验
    no_annotations_string_list = no_annotations_string.split('\n')
    temp_list = []
    for line in no_annotations_string_list:
        if line.strip() == '':
            continue
        match_res = re.search(split_regx, line)
        if match_res is not None:
            # 包含创建数据库语句
            if match_res.group(1) is not None:
                raise ValueError('create database key word find, error')
            # 包含use 数据库语句
            if match_res.group(2) is not None:
                raise ValueError('use databse key word find, error')
            # ===========这里可以一定程度保证存储过程和函数在sql_delimiter_list中
            # 包含insert语句
            if match_res.group(3) is not None:
                insert_list.append(match_res.group(3))
                continue
            # 包含update语句
            if match_res.group(4) is not None:
                update_list.append(match_res.group(4))
                continue
            # 包含alter语句
            if match_res.group(5) is not None:
                alter_list.append(match_res.group(5))
                continue
            # 包含delete from语句
            if match_res.group(6) is not None:
                delete_list.append(match_res.group(6))
                continue
            # 包含truncate table语句
            if match_res.group(7) is not None:
                truncate_list.append(match_res.group(7))
                continue
            # 包含PROCEDURE|FUNCTION|trigger语句
            # 这些语句必须被包含在上边已经处理过的DELIMITER语句中,否则报错
            if match_res.group(8) is not None:
                raise ValueError('CREATE PROCEDURE|FUNCTION|TRIGGER not between two DELIMITER')
            # 包含DEFINER=字段
            if match_res.group(11) is not None:
                if re.search(view_regx, line) is not None:
                    view_sql_list.append(re.sub(view_regx, 'CREATE VIEW', line))
                    continue
                else:
                    raise ValueError('DEFINER key word find')
            # 表drop语句
            if match_res.group(12) is not None:
                drop_table_list.append(match_res.group(12))
                continue
            # drop database 语句
            if match_res.group(13) is not None:
                raise ValueError('drop database sql find')
            # 其他drop语句
            if match_res.group(14) is not None:
                if re.search(drop_incolum_regx, line):
                    if temp_list:
                        temp_list.append(line)
                        sql_string = ' '.join(temp_list)
                        temp_list = []
                        if re.match(alter_table_regx, sql_string):
                            alter_list.append(sql_string)
                            continue
                        else:
                            raise ValueError('drop COLUMN|PRIMARY|KEY|INDEX with not start with alter table')
                    else:
                        raise ValueError('drop COLUMN|PRIMARY|KEY|INDEX with temp list empty')
                other_drop_list.append(match_res.group(14))
                continue
            # 匹配到结束符号;
            if match_res.group(15) is not None:
                temp_list.append(line)
                # 合并成sql语句
                sql_string = '\n'.join(temp_list)
                temp_list = []
                # sql语句检查
                create_match = re.match(create_table_regx, sql_string)
                if create_match is None:
                    sql_string = sql_string.replace('\n', ' ')
                    if re.match(alter_table_regx, sql_string):
                        alter_list.append(sql_string)
                        continue
                    elif re.match(replace_and_insert_regx, sql_string):
                        insert_list.append(sql_string)
                        continue
                    else:
                        raise ValueError('sql [%s] not sql of create table or view alter' % sql_string)
                # 发现多个create在当前语句中
                if create_match.group(2) is not None:
                    raise ValueError('sql [%s] find over one create in one' % sql_string)
                # 创建的是view
                if create_match.group(1).lower() == 'view':
                    view_sql_list.append(sql_string)
                else:
                    create_list.append(sql_string)
                continue
        # 除去auto_increment
        line = re.sub(auto_increment_regx, '', line)
        temp_list.append(line)
    full_string_list = list(set(other_drop_list))
    if drop_table:
        full_string_list += drop_table_list
    full_string_list = full_string_list + create_list + alter_list + view_sql_list
    if len(sql_delimiter_list) > 0:
        # 插入源文件中DELIMITER包含的内容
        full_string_list += sql_delimiter_list
    if with_data:
        full_string_list = full_string_list + truncate_list + delete_list + insert_list + update_list
    if len(full_string_list) == 0:
        raise ValueError('no sql line find in file')
    return full_string_list
