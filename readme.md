simple file share
===========

解决内网机器之间文件共享和传输的小工具，类似安装包下载的场景。为了复用基础设施，可以用 wget, curl来调用接口，只要提供一个简单的上传接口即可。

* [ ] 文件直传，存到指定目录
* [ ] 接口，list，上传，下载

默认的存储目录是 `/tmp`

使用方式

上传
```
curl -v -F "file=@t.txt" "http://localhost:8080/"
```

下载
```
curl http://localhost:8080/t.txt > tt.txt
```

