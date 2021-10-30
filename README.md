
# NEW VERSION 2.0 at https://github.com/upulkkis/Score-Tool-2.0 

# Score Tool (old version)
An orchestration analysis tool for composers, conductors, musicians and music theorists.
Copyright (c) 2020 Uljas Pulkkis.

## How do I use it?
This is an app for analyzing orchestral scores in your browser. You can use it online or install with pip and launch from your own machine.

### Online version of score-tool supported by the Sibelius Academy of Music:
This repo, old version: https://old.score-tool.com

(new 2.0 version (new repo): https://score-tool.com)

### Local – pip
```bash
$ pip3 install orchestration-analyzer
$ score-tool
# Go to localhost:8050 on your browser
```

### Local – Docker (Thank you, Seyoung Park, for Docker!)
```bash
$ git clone git@github.com:upulkkis/Score-Tool.git
$ cd Score-Tool
$ make docker-build
$ make docker-run
# Go to localhost:8050 on your browser
```

### Local – Native
```bash
$ git clone git@github.com:upulkkis/Score-Tool.git
# (or withouth ssh: git clone https://github.com/upulkkis/Score-Tool.git)
$ cd Score-Tool
$ pip3 install -r requirements.txt
$ python3 score-tool.py
# Go to localhost:8050 on your browser
```
