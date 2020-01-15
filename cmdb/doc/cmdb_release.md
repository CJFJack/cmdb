# CMDB 部署文档

- 版本： v20191101
- 相关备份文件在 192.168.40.21



### 安装 Python

从192.168.100.66的`/data/source`上拷贝*Python-3.5.2.tgz*到本地管理机，执行如下的命令

```shell
cd /data/source && tar xvf Python-3.5.2.tgz -C /usr/local/src/ && cd /usr/local/src/Python-3.5.2 && ./configure --prefix=/usr/local/python3.5.2 && make && make install
```



### Python 虚拟环境

在192.168.100.66的`/data/code/`目录下，将`cy_devops`整个目录拷贝到本地管理机**同样的目录下**

```shell
cd /data/code/cy_devops
```



### nginx

- 安装nginx

- 关闭selinux

- ssl文件

- 配置文件

  ```shell
vim cmdb.conf
  ```
  
  ```shell
  # cmdb nginx conf
  
  # configuration of the server
  server {
      # the port your site will be served on
      listen      80;
      # the domain name it will serve for
      server_name cmdb.cy666.com 192.168.100.66; # substitute your machine's IP address or FQDN
      # forced jump https
  	#rewrite ^(.*) https://$server_name$1 permanent;
  	#rewrite ^(.*) https://cmdb.cy666.com$1 permanent;
      charset     utf-8;
      access_log  /data/logs/nginx/cmdb_access.log main;
  
      # max upload size
      client_max_body_size 75M;   # adjust to taste
  
      # Django media
  
      location /static {
          alias /data/www/cmdb/cmdb/static; # your Django project's static files - amend as required
      }
  
  	location /workflow_doc {
          alias /data/www/workflow_doc; # your Django project's static files - amend as required
      }
  
      location /downloads {
          alias /data/www/cmdb/it_assets/downloads; # your Django project's static files - amend as required
      }
  
      location /usersdownloads {
          alias /data/www/cmdb/users/downloads;
      }
  
  	location /hotupdate_download {
          alias /data/www/cmdb/myworkflows/hotupdate_download;
      }
  
       location /host_download {
          alias /data/www/cmdb/assets/host_download;
      }
  
      # Finally, send all non-media requests to the Django server.
      location / {
  		uwsgi_read_timeout 120;
          uwsgi_pass  0.0.0.0:8080;
          include     /data/www/cmdb/uwsgi_params; # the uwsgi_params file you installed
      }
  
  
  
  	location /ws {
  		proxy_pass http://0.0.0.0:8081;
  		proxy_http_version 1.1;
  		proxy_set_header Upgrade $http_upgrade;
  		proxy_set_header Connection "upgrade";
  		proxy_redirect     off;
  		proxy_set_header   Host $host;
  		proxy_set_header   X-Real-IP $remote_addr;
  		proxy_set_header   X-Forwarded-For $proxy_add_x_forwarded_for;
  		proxy_set_header   X-Forwarded-Host $server_name;
  		proxy_read_timeout  36000s;
  		proxy_send_timeout  36000s;
  	}
  }
  
  server {
      # the port your site will be served on
      listen      443 ssl;
      # the domain name it will serve for
      server_name cmdb.cy666.com 192.168.100.66; # substitute your machine's IP address or FQDN
      charset     utf-8;
      access_log  /data/logs/nginx/cmdb_access.log main;
  
      # max upload size
      client_max_body_size 75M;   # adjust to taste
  
  
  	# configuration for https
  	ssl_protocols       TLSv1 TLSv1.1 TLSv1.2;
  	ssl_ciphers         AES128-SHA:AES256-SHA:RC4-SHA:DES-CBC3-SHA:RC4-MD5;
  	ssl_certificate     /usr/local/nginx/ssl/nginx.crt;
  	ssl_certificate_key /usr/local/nginx/ssl/nginx.key;
  	ssl_session_cache   shared:SSL:10m;
  	ssl_session_timeout 10m;
  
  
      # Django media
  
      location /static {
          alias /data/www/cmdb/cmdb/static; # your Django project's static files - amend as required
      }
  
      location /downloads {
          alias /data/www/cmdb/it_assets/downloads; # your Django project's static files - amend as required
      }
  
      location /usersdownloads {
          alias /data/www/cmdb/users/downloads;
      }
  
  	location /hotupdate_download {
          alias /data/www/cmdb/myworkflows/hotupdate_download;
      }
  
  	location /host_download {
          alias /data/www/cmdb/assets/host_download;
      }
  
      # Finally, send all non-media requests to the Django server.
      location / {
          uwsgi_pass  0.0.0.0:8080;
          include     /data/www/cmdb/uwsgi_params; # the uwsgi_params file you installed
      }
  
  	location /ws {
  		proxy_pass http://0.0.0.0:8081;
  		proxy_http_version 1.1;
  		proxy_set_header Upgrade $http_upgrade;
  		proxy_set_header Connection "upgrade";
  		proxy_redirect     off;
  		proxy_set_header   Host $host;
  		proxy_set_header   X-Real-IP $remote_addr;
  		proxy_set_header   X-Forwarded-For $proxy_add_x_forwarded_for;
  		proxy_set_header   X-Forwarded-Host $server_name;
  		proxy_read_timeout  36000s;
  		proxy_send_timeout  36000s;
  	}
  }

  ```

  jenkins_40_8.conf
  
  ```shell
  vim jenkins_40_8.conf
  ```
  
  ```nginx
  server
  {
      # 用于解决从cmdb跳转到jenkins时cookie不能携带的跨域问题
      listen 8091;
      server_name 192.168.100.66 cmdb.cy666.com;
      location / {
          proxy_pass http://192.168.40.8:8088;
  
          add_header Access-Control-Allow-Methods *;
          add_header Access-Control-Max-Age 3600;
          add_header Access-Control-Allow-Credentials true;
        add_header Access-Control-Allow-Origin $http_origin;
          add_header Access-Control-Allow-Headers
        $http_access_control_request_headers;
      }
  }
  ```
  
  jenkins_40_15.conf 
  
  ```shell
  vim jenkins_40_15.conf 
  ```
  
  ```nginx
  server
  {
      # 用于解决从cmdb跳转到jenkins时cookie不能携带的跨域问题
      listen 8092;
      server_name 192.168.100.66 cmdb.cy666.com;
      location / {
          proxy_pass http://192.168.40.15:8080;

          add_header Access-Control-Allow-Methods *;
        add_header Access-Control-Max-Age 3600;
          add_header Access-Control-Allow-Credentials true;
          add_header Access-Control-Allow-Origin $http_origin;
          add_header Access-Control-Allow-Headers
          $http_access_control_request_headers;
      }
  }
  ```
  
  zabbix.conf
  
  ```shell
  vim zabbix.conf
  ```
  
  ```nginx
  server
  {
      # 用于解决从cmdb跳转到zabbix时cookie不能携带的跨域问题
    listen 8094;
      server_name 192.168.100.66 cmdb.cy666.com;
      location / {
          proxy_pass http://monitor.chuangyunet.com;
  
          add_header Access-Control-Allow-Methods *;
          add_header Access-Control-Max-Age 3600;
          add_header Access-Control-Allow-Credentials true;
          add_header Access-Control-Allow-Origin $http_origin;
          add_header Access-Control-Allow-Headers
          $http_access_control_request_headers;
      }
  }
  ```
  
  

### uwsgi

- 配置uwsgi启动、停止、重启方法

  ```shell
  vim cat /etc/init/uwsgi.conf 
  ```

  ```shell
  description "uWSGI Emperor"
  start on runlevel [2345]
  stop on runlevel [!2345]
  respawn
  exec /data/code/cy_devops/bin/uwsgi --emperor /etc/uwsgi/vassals/ --logto /var/log/cmdb.log
  ```

- 创建uwsgi配置文件

  ```shell
  vim /etc/uwsgi/vassals/uwsgi.ini 
  ```

  ```shell
  [uwsgi]
  socket = 0.0.0.0:8080
  processes = 8
  threads = 10
  listen = 2048
  chdir = /data/www/cmdb/
  pythonpath = /data/code/cy_devops/bin/python
  env = DJANGO_SETTINGS_MODULE=cmdb.settings
  env = LANG=en_US.UTF-8
  env LC_ALL=en_US.UTF-8
  env LC_LANG=en_US.UTF-8
  module = django.core.wsgi:get_wsgi_application()
  daemonize = /var/log/cmdb.log
  pidfile = /tmp/cmdb.pid
  buffer-size  = 11018
  log-maxsize = 20000000
  #disable-logging = true
  ```

- 修改系统最大连接数

  ```shell
  echo 8912 > /proc/sys/net/ipv4/tcp_max_syn_backlog
  echo 8912 > /proc/sys/net/core/somaxconn
  ```

- 开启、停止、重启方法

  ```shell
  initctl start|stop|restart uwsgi
  ```



### daphne

- 创建daphnei.conf

```shell
vim /etc/init/daphnew.conf
```

```shell
start on runlevel [2345]
stop on runlevel [016]

respawn

script
    cd /data/www/cmdb
    export DJANGO_SETTINGS_MODULE="cmdb.settings"
    exec /data/code/cy_devops/bin/daphne -b 0.0.0.0 -p 8081 --access-log /var/log/daphne-interface.log  cmdb.asgi:channel_layer
end script
```

- 创建daphnew.conf

```shell
vim /etc/init/daphnew.conf
```

```shell
start on runlevel [2345]
stop on runlevel [016]

respawn

script
    cd /data/www/cmdb
    export DJANGO_SETTINGS_MODULE="cmdb.settings"
    exec /data/code/cy_devops/bin/python manage.py runworker --threads 100  -v2
end script
```

- 开启、停止、重启方法

```shell
initctl start|stop|restart daphnei
initctl start|stop|restart daphnew
```



### mysql

- 安装mysql

- 设置密码

- 创建数据库

  ```mysql
  CREATE DATABASE cmdb DEFAULT CHARACTER SET utf8;
  ```

- 还原cmdb数据库

- 修改cmdb数据库配置

  ```shell
  vim /data/www/cmdb/cmdb/settings.py
  ```

  ```python
  DATABASES = {
      'default': {
          'ENGINE': 'django.db.backends.mysql',
          'NAME': 'cmdb',
          'USER': 'root',
          'PASSWORD': 'test',
          'HOST': '127.0.0.1',
          'PORT': '3306',
      }
  }
  ```

  

### redis

- 安装redis

- 设置密码

- 修改cmdb redis配置

  ```shell
  vim /data/www/cmdb/cmdb/settings.py
  ```

  ```python
  REDIS_URL = 'redis://:<password>@localhost:6379/0'
  REDIS_HOST = 'localhost'
  REDIS_PORT = 6379
  REDIS_PASSWORD = '<password>'
  REDIS_BACKEND_URL = 'redis://:<password>@localhost:6379/1'
  ```

  

### cmdb代码

```shell
/data/www/cmdb
```



### celery

配置文件路径

```shell
cd /etc/default/
```

启动文件路径

```shell
cd /etc/init.d/
```



### crontab

```shell
*/30 * * * *  /usr/sbin/ntpdate 192.168.40.8 > /dev/null 2>&1
*/10 * * * * /data/code/cy_devops/bin/python3 /data/www/cmdb/celery_worker_monitor.py
*/5 * * * * /data/code/cy_devops/bin/python3 /data/www/cmdb/check_host_crontab_task.py
*/5 * * * * /data/code/cy_devops/bin/python3 /data/www/cmdb/check_gameserver_crontab_task.py
*/5 * * * * /data/code/cy_devops/bin/python3 /data/www/cmdb/check_abnormal_workflow.py
*/10 * * * * /data/code/cy_devops/bin/python3 /data/www/cmdb/check_version_update_task.py
```



### 开机启动

```shell
vim /etc/rc.d/rc.local 
```

```shell
#!/bin/sh
#
# This script will be executed *after* all the other init scripts.
# You can put your own initialization stuff in here if you don't
# want to do the full Sys V style init stuff.

touch /var/lock/subsys/local
echo "deadline" > /sys/block/sda/queue/scheduler
echo "deadline" > /sys/block/sda/queue/scheduler

# 启动redis
/usr/bin/redis-server /etc/redis.conf
# 启动nginx
/usr/local/nginx/sbin/nginx

# 启动celery beat
/etc/init.d/celerybeat start

# 启动几个celeryworker
/etc/init.d/add-server-permission-worker start
/etc/init.d/add-svn-worker start
/etc/init.d/clean-project-serper-worker start
/etc/init.d/hotupdate-worker start
/etc/init.d/hotupdate-tiemout-worker start
/etc/init.d/recieve-mail-worker start
/etc/init.d/send-mail-worker start
/etc/init.d/shost-beat-worker start
/etc/init.d/sqq-worker start
/etc/init.d/add-mysql-permission-worker start
/etc/init.d/remove-mysql-permission-worker start
/etc/init.d/add-qq-user-worker start
/etc/init.d/add-email-account-worker start
/etc/init.d/add-mac-worker start
/etc/init.d/send-wx-worker start
/etc/init.d/execute-salt-task-worker start
/etc/init.d/refresh-cdn-worker start
/etc/init.d/game-server-action-worker start
/etc/init.d/host-migrate-worker start
/etc/init.d/host-recover-worker start
/etc/init.d/cancel-workflow-worker start
/etc/init.d/send-wx-taskcard-worker start
/etc/init.d/wx-whitelist-worker start
/etc/init.d/host-initialize-worker start
/etc/init.d/version-update-worker start
/etc/init.d/txcloud-api-worker start

# 开启刷新热更新日志到前端页面脚本
nohup /data/code/cy_devops/bin/python /data/www/cmdb/cmdb_update_loop_log.py > /dev/null 2>&1 &
```











