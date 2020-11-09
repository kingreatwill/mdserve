# mdserve
markdown server.

## pip
pip install --upgrade mdserve -i https://pypi.org/simple/


## docker
docker build -t mdserve:git -f ./dockerfile .
docker run -it -p 8080:8080 -v /root/docker/mdserve:/usr/share/mdserve mdserve:git

## Upgrade
### v1.1.0
add git pull