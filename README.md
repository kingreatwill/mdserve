# mdserve
markdown server.

## pip
```
pip install --upgrade mdserve -i https://pypi.org/simple/
```

## docker
```
docker build -t mdserve:git -f ./dockerfile .

docker run -it -p 8080:8080 -v /f/github/openjw/open:/usr/share/mdserve mdserve:git
```
