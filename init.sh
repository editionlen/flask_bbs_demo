#需要确保安装python3
#创建python3虚拟环境
virtualenv -p /usr/bin/python3 py3env
#进入虚拟环境
source py3env/bin/activate
#需要在虚拟环境执行安装库
pip install flask
pip install flask_sqlalchemy
pip install flask_script
pip install flask_migrate
pip install pymysql
#初始化数据库
python manage.py db init
python manage.py db migrate
python manage.py db upgrade