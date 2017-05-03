simpleservice
=============

主要代码基于Openstack Mitaka中的oslo_messaging与oslo_service

相关依赖都移至simpleutil中

删除线程相关代码,统一使用eventlet

删除线程兼容的写法

替换大部分线程锁为协程锁,重写一些特殊的锁,具体参考simpleutil说明文件

代码瘦身,删除部分兼容pytho 2、3的代码,支持python2.6+

删除部分动态加载代码,驱动只支持kombu + py-ampy

删除Transport层,相关内容合并到Driver层

Target中的namespace用于区分不同endpoint,version属性无用化

Dispatcher分发部分修改,支持多endpoint

Windows兼容代码试用于调试环境,不建议直接使用