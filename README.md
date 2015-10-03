wofu
======================
Gate way of Mesos POC

Build Docker image and try
--------------------------
1. git clone https://github.com/Intel-bigdata/wofu.git
2. cd wofu && docker build -t intel/wofu ./
3. docker run -it --rm -p 8000:8000 intel/wofu
4. Browse http://<host_IP>:8000 to play with it
