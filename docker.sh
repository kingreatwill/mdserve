docker build --no-cache -t mdserve:1.4 -f ./dockerfile .
docker stop mdserve
docker rm mdserve
docker run -itd -p 8001:8080 -v /root/github/open:/usr/share/mdserve --name mdserve mdserve:1.4