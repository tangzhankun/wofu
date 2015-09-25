FROM ubuntu:14.04
MAINTAINER Zhankun Tang "zhankun.tang@intel.com"
RUN export https_proxy=http://shzintpr01.sh.intel.com:913 && export export http_proxy=http://shzintpr01.sh.intel.com:913 && apt-get update && apt-get install -y python-pip && apt-get install -y python-dev && pip install django && pip install wrapt && pip install netifaces && pip install python-novaclient
ENTRYPOINT ["/bin/bash"]
