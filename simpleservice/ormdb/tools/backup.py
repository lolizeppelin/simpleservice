import os
import sys
import subprocess

from simpleutil.log import log as logging
from simpleutil.utils import systemutils

LOG = logging.getLogger(__name__)

try:
    MYSQLDUMP = systemutils.find_executable('mysqldump')
    MYSQL = systemutils.find_executable('mysql')
    GZIP = systemutils.find_executable('gzip')
    UNGZIP = systemutils.find_executable('gunzip')
except NotImplementedError:
    if not systemutils.WINDOWS:
        raise

if systemutils.LINUX:
    from simpleutil.utils.systemutils import posix

    wait = posix.wait
else:
    wait = systemutils.subwait


def _mysqldump_to_gz(dumpfile,
                     host, port, user, passwd, schema,
                     character_set=None, extargs=None,
                     logfile=None, callable=None, timeout=None):
    character_set = character_set or 'utf8'
    logfile = logfile or os.devnull
    timeout = timeout or 3600

    dump_args = [MYSQLDUMP,
                 '--default-character-set=%s' % character_set, ]
    if extargs:
        dump_args.extend(extargs)
    dump_args.extend(['-u%s' % user, '-p%s' % passwd,
                      '-h%s' % host, '-P%d' % port, schema])
    gz_args = [GZIP, '-c', '-q']
    LOG.debug(' '.join(dump_args))

    with open(logfile, 'wb') as log:
        with open(dumpfile, 'wb') as f:
            r, w = os.pipe()
            if systemutils.LINUX:
                fork = callable or os.fork
                dup_proc = fork()
                if dup_proc == 0:
                    os.dup2(w, sys.stdout.fileno())
                    os.close(w)
                    os.dup2(log.fileno(), sys.stderr.fileno())
                    try:
                        os.execv(MYSQLDUMP, dump_args)
                    except OSError:
                        os._exit(1)
                os.close(w)
                gz_proc = fork()
                if gz_proc == 0:
                    os.dup2(r, sys.stdin.fileno())
                    os.close(r)
                    os.dup2(f.fileno(), sys.stdout.fileno())
                    os.dup2(log.fileno(), sys.stderr.fileno())
                    try:
                        os.execv(GZIP, gz_args)
                    except OSError:
                        os._exit(1)
                os.close(r)
            else:
                dup_proc = subprocess.Popen(executable=MYSQLDUMP, args=dump_args,
                                            stdout=w,
                                            stderr=log.fileno(),
                                            preexec_fn=callable)
                os.close(w)
                gz_proc = subprocess.Popen(executable=GZIP, args=gz_args,
                                           stdin=r,
                                           stdout=f.fileno(),
                                           stderr=log.fileno(),
                                           preexec_fn=callable)
                os.close(r)
    try:
        wait(dup_proc, timeout)
    except OSError:
        LOG.error('wait mysql dump sub process catch error')
    except (systemutils.UnExceptExit, systemutils.ExitBySIG):
        LOG.error('mysql dump exit code error or killed')
    wait(gz_proc, timeout)


def _mysqldump(dumpfile,
               host, port, user, passwd, schema,
               character_set=None, extargs=None,
               logfile=None, callable=None, timeout=None):
    character_set = character_set or 'utf8'
    logfile = logfile or os.devnull
    timeout = timeout or 3600

    dump_args = [MYSQLDUMP,
                 '--default-character-set=%s' % character_set, ]
    if extargs:
        dump_args.extend(extargs)
    dump_args.extend(['-u%s' % user, '-p%s' % passwd,
                      '-h%s' % host, '-P%d' % port, schema])
    LOG.debug(' '.join(dump_args))

    with open(logfile, 'wb') as log:
        with open(dumpfile, 'wb') as f:
            if systemutils.LINUX:
                fork = callable or os.fork
                dup_proc = fork()
                if dup_proc == 0:
                    os.dup2(f.fileno(), sys.stdout.fileno())
                    os.dup2(log.fileno(), sys.stderr.fileno())
                    try:
                        os.execv(MYSQLDUMP, dump_args)
                    except OSError:
                        os._exit(1)
            else:
                dup_proc = subprocess.Popen(executable=MYSQLDUMP, args=dump_args,
                                            stdout=f.fileno(),
                                            stderr=log.fileno(),
                                            preexec_fn=callable)
    wait(dup_proc, timeout)


def _mysqlload_from_gz(loadfile, host, port, user, passwd, schema,
                       character_set=None, extargs=None,
                       logfile=None, callable=None, timeout=None):
    character_set = character_set or 'utf8'
    logfile = logfile or os.devnull
    timeout = timeout or 3600

    load_args = [MYSQL, '--default-character-set=%s' % character_set]
    if extargs:
        load_args.extend(extargs)
    load_args.extend(['-u%s' % user, '-p%s' % passwd,
                      '-h%s' % host, '-P%d' % port,
                      schema])
    ungz_args = [UNGZIP, '-c', '-q', loadfile]
    LOG.debug(' '.join(load_args))

    with open(logfile, 'wb') as log:
        r, w = os.pipe()
        if systemutils.LINUX:
            fork = callable or os.fork
            ungz_proc = fork()
            if ungz_proc == 0:
                os.dup2(w, sys.stdout.fileno())
                os.close(w)
                os.dup2(log.fileno(), sys.stderr.fileno())
                try:
                    os.execv(UNGZIP, ungz_args)
                except OSError:
                    os._exit(1)
            os.close(w)
            load_proc = fork()
            if load_proc == 0:
                os.dup2(r, sys.stdin.fileno())
                os.close(r)
                os.dup2(log.fileno(), sys.stderr.fileno())
                os.close(log.fileno())
                try:
                    os.execv(MYSQL, load_args)
                except OSError:
                    os._exit(1)
            os.close(r)
        else:
            ungz_proc = subprocess.Popen(executable=UNGZIP, args=ungz_args,
                                         stdout=w,
                                         stderr=log.fileno(),
                                         preexec_fn=callable)
            os.close(w)
            load_proc = subprocess.Popen(executable=MYSQL, args=load_args,
                                         stdin=r,
                                         stdout=log.fileno(),
                                         stderr=log.fileno(),
                                         preexec_fn=callable)
            os.close(r)
    try:
        wait(ungz_proc, timeout)
    except OSError:
        LOG.error('wait gunzip sub process catch error')
    except (systemutils.UnExceptExit, systemutils.ExitBySIG):
        LOG.error('gunzip exit code error or killed')
    wait(load_proc, timeout)


def _mysqlload(loadfile, host, port, user, passwd, schema,
               character_set=None, extargs=None,
               logfile=None, callable=None, timeout=None):
    character_set = character_set or 'utf8'
    logfile = logfile or os.devnull
    timeout = timeout or 3600

    load_args = [MYSQL, '--default-character-set=%s' % character_set]
    if extargs:
        load_args.extend(extargs)
    load_args.extend(['-u%s' % user, '-p%s' % passwd,
                      '-h%s' % host, '-P%d' % port,
                      schema])
    LOG.debug(' '.join(load_args))

    with open(logfile, 'wb') as log:
        with open(loadfile, 'rb') as f:
            if systemutils.LINUX:
                fork = callable or os.fork
                load_proc = fork()
                if load_proc == 0:
                    os.dup2(f.fileno(), sys.stdin.fileno())
                    os.dup2(log.fileno(), sys.stderr.fileno())
                    os.close(log.fileno())
                    try:
                        os.execv(MYSQL, load_args)
                    except OSError:
                        os._exit(1)
            else:
                load_proc = subprocess.Popen(executable=MYSQL, args=load_args,
                                             stdin=f.fileno(),
                                             stdout=log.fileno(),
                                             stderr=log.fileno(),
                                             preexec_fn=callable)
    wait(load_proc, timeout)


def mysqlload(loadfile, host, port, user, passwd, schema,
              character_set=None, extargs=None,
              logfile=None, callable=None, timeout=None):
    if loadfile.endswith('.gz'):
        _mysqlload_from_gz(loadfile, host, port, user, passwd, schema,
                           character_set, extargs,
                           logfile, callable, timeout)
    else:
        _mysqlload(loadfile, host, port, user, passwd, schema,
                   character_set, extargs,
                   logfile, callable, timeout)


def mysqldump(dumpfile,
              host, port, user, passwd, schema,
              character_set=None, extargs=None,
              logfile=None, callable=None, timeout=None):
    if dumpfile.endswith('.gz'):
        _mysqldump_to_gz(dumpfile, host, port, user, passwd, schema,
                         character_set, extargs,
                         logfile, callable, timeout)
    else:
        _mysqldump(dumpfile, host, port, user, passwd, schema,
                   character_set, extargs,
                   logfile, callable, timeout)
