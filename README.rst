simpleservice
=============

模仿openstack写的服务框架,对内rpc通信,对外提供http restful接口

主要代码基于Openstack Mitaka中的oslo_messaging与oslo_service与oslo_db

wsig部分代码来源于keyston和neutron

尽量统一rpc service和wsig service的写法

尽量统一route的写法

相关依赖都移至simpleutil中

删除线程相关代码

删除线程兼容相关代码

原多线相关代码统一使用eventlet

替换大部分线程锁为协程锁,重写一些特殊的锁,具体参考simpleutil说明文件

代码瘦身,删除部分兼容python 2、3的代码,支持python2.6+

删除部分动态加载代码,驱动只支持kombu + py-ampy

删除Transport层,相关内容合并到Driver层

Target中的namespace用于区分不同endpoint,version属性无用化

Dispatcher分发部分修改,支持多endpoint

Windows兼容代码用于调试业务代码,不建议直接使用