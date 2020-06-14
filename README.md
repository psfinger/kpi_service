# 构建开发环境kpi_service
## （可选）从头开始构建kpi_service runtime
```
conda create -n kpi_service --clone base
conda activate kpi_service
pip install flask
pip install flask_cors
pip install flask-restful
pip install gunicorn
pip install greenlet
pip install gevent
```

# kpi_service部署

## 创建用户 & 通过堡垒root账户上传介质
```
检查介质zip文件布局：
kpi_service/bin/Miniconda3-latest-Linux-x86_64.sh
kpi_service/bin/runtime.tar.gz
kpi_service/kpi_service.py

ssh客户端执行：useradd kpi_service

通过winscp上传介质 kpi_service-xxx-xxx.zip 到 /home/kpi_service 目录

chown kpi_service:kpi_service /home/kpi_service/kpi_service-xxx-xxx.zip
```
## 解压介质安装kpi_service应用
```
su - kpi_service
unzip /home/kpi_service/kpi_service-xxx-xxx.zip
exit
```

## 安装python3虚拟环境
```
su - kpi_service
sh kpi_service/bin/Miniconda3-latest-Linux-x86_64.sh
选项：<ENTER,yes,ENTER,yes>
exit
su - kpi_service
conda config --set auto_activate_base false
exit
```
## 安装kpi_service运行时
```
su - kpi_service
cd kpi_service/bin
tar xf runtime.tar.gz
mv kpi_service /home/kpi_service/miniconda3/envs
exit
```

## 启动kpi_service
```
su - kpi_service
conda activate kpi_service
cd kpi_service
echo "{}" > store
echo "{}" > mivs_storev2
echo "{}" > cdms_storev2
nohup gunicorn -w 1 -k gevent --worker-connections 30000 -b 0.0.0.0:3000 kpi_service:app &
(可选)nohup gunicorn -w 1 -k gevent --worker-connections 30000 -b 0.0.0.0:3000 kpi_service:app --certfile=server.crt --keyfile=server.key &
exit
```

## 检查kpi_service
```
netstat -nplt | grep 3000
tcp        0      0 0.0.0.0:3000            0.0.0.0:*               LISTEN      <26479>/python

curl -H "Content-Type:application/json" -X GET http://portal.buaiti.com:3000/service/cdms/kpis
curl -H "Content-Type:application/json" -X GET http://portal.buaiti.com:3000/service/mivs/kpis
{}
```

## 回退
```
userdel kpi_service
echo "rm -rf \$1" > myrm.sh
sh myrm.sh /home/kpi_service
sh myrm.sh myrm.sh
```

# kpi_service接口
## 1 写入kpi：
写入kpi接口`request`：
```
curl -H "Content-Type:application/json" -X PUT -d '{"kpi": "kpi1", "group": ["业务量"], "data": [[1000]]}' http://portal.buaiti.com:3000/service/cdms/kpi1
curl -H "Content-Type:application/json" -X PUT -d '{"kpi": "kpi1", "group": ["业务量"], "data": [[1000]]}' http://portal.buaiti.com:3000/service/mivs/kpi1
```

写入kpi接口`response`： 成功`200`，其他为不成功
```
{
"kpi": "kpi1", "group": ["业务量"], "data": [[1000]]
}
```

## 2 读取kpi：
读取kpi接口`request`：
```
curl -H "Content-Type:application/json" -X GET http://portal.buaiti.com:3000/service/cdms/kpi1
curl -H "Content-Type:application/json" -X GET http://portal.buaiti.com:3000/service/mivs/kpi1
```

读取kpi接口`response`：成功`200`，其他为不成功
```
{
"kpi": "kpi1", "group": ["业务量"], "data": [[1000]]
}
```

## 3 读取所有kpi：
读取所有kpi接口 `request`：
```
curl -H "Content-Type:application/json" -X GET http://portal.buaiti.com:3000/service/cdms/kpis
curl -H "Content-Type:application/json" -X GET http://portal.buaiti.com:3000/service/mivs/kpis
```

读取所有kpi接口`response`：成功`200`，其他为不成功
```
{
"kpi1": {"kpi": "kpi1", "group": ["业务量"], "data": [[1000]]}, 
"kpi2": {"kpi": "kpi2", "group": ["笔数", "金额"], "data": [[100, 2101.23]]}, 
"kpi3": {"kpi": "kpi3", "group": ["工行", "农行", "建行"], "data": [[100, 80, 88], [100, 200, 300]]}
}
```

## 4 删除kpi：
删除kpi接口 `request`：
```
curl -X DELETE http://portal.buaiti.com:3000/service/cdms/kpi1
curl -X DELETE http://portal.buaiti.com:3000/service/mivs/kpi1
```

删除kpi接口 response：成功`200`，其他为不成功
```
{"status": 1}
```
