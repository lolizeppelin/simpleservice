import sqlalchemy

from simpleservice.ormdb.engines import create_engine

dst = {'host': '172.20.0.3',
       'port': 3304,
       'schema': 'manager',
       'user': 'root',
       'passwd': '111111'}

engine = create_engine(dst)

cloum_types = [sqlalchemy.UnicodeText, ]


def get(engine, cloum):
    return engine.dialect.type_descriptor(cloum)


for cloum in cloum_types:
    ret = get(engine, cloum)
    print ret, type(ret)
    for attr in dir(ret):
        print attr, getattr(ret, attr)