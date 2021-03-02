# List-based phishing detection

In this repository, you will find a simple white list-based phishing detection.

To that, you need to train a spacy model to extract key-words from an SMS message. The file [train_scapy.py](https://github.com/stephanefschwarz/PhishingListBased/blob/master/train_spacy.py) contains the step-by-step procedure.


To run the list-based framework, look at the [check_white_list.py](https://github.com/stephanefschwarz/PhishingListBased/blob/master/check_white_list.py) file.


## Docker

Building a Docker image from Dockerfile

### RUN on the shell

```shell
$ cd /path/to/URLPhishing/DOCKERFILE/
$ docker build -t whitephish:latest .
```

and then run the container:

```shell
$ nvidia-docker run --tty --interactive --userns=host --volume /path/to/URLPhishing:/home/<your-name>/work --name <container-name> whitephish:latest  /bin/bash


```