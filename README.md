# mdserve
markdown server.

## pip
```
pip install --upgrade mdserve -i https://pypi.org/simple/
```

## docker
```
docker build -t mdserve:1.4 -f ./dockerfile .

docker run -it -p 8080:8080 -v /f/github/openjw/open:/usr/share/mdserve mdserve:1.4
docker run -itd -p 8001:8080 -v /root/github/open:/usr/share/mdserve mdserve:1.4
```
