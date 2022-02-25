### celery
#### 启动celery
celery -A shopping worker -l info
celery -A shopping beat

#### 启动某一个queue
celery worker -Q statistics_platform_data --loglevel=info

### 系统选择Ubuntu16.04
#### pip安装MySQL-python出现 (/usr/bin/ld: cannot find -lssl)
> 1.使用sudo apt-cache search libxxx ,搜索出libxxx-dev, 然后安装sudo apt-get install libxxx-dev

#### uwsgi 报错unavailable modifier requested: 0
> apt-get install uwsgi-plugin-python