### Introduction

mini-grader is a mini grader for programming competition tasks, especially for
contests with downloadable test data (but no online grader).

mini-grader tries to guess as much as possible about the environment in order
to make it easy to quickly run your program on all test data.  To use, roughly
point it at the location of test data and tell it the executable to run.  For
example:

    mini-grader.py --test-data-dir=.. ./twofive.exe

In the above example, mini-grader might:
* Find test cases in ../testdata/twofive/twofive_*.in
* Run ./twofive.exe on all 20 test cases
* Enforce a time limit of 1 second (configurable)
* Enforce a memory limit of 256 MB (configurable)
* Produce cute coloured output

![Screenshot](https://raw.github.com/lovrop/mini-grader/master/screenshot.png)

### Requirements

* Python 3.2 or newer
* Linux or Windows
