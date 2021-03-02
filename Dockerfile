FROM pytorch/pytorch

RUN apt update
RUN apt install nano
RUN apt-get install -y git 
RUN apt-get install -y wget 

RUN apt update

RUN pip install --upgrade pip 
RUN pip install pandas
RUN pip install numpy
RUN pip install tldextract
RUN pip install spacy

