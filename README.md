## Rainbow Stream
Terminal-based Twitter Client with Streaming API support. 
Realtime tweetstream, compose, search ... and much more fun directly from terminal.
Only supports Python 2.7 or later.

This package build on the top of [Python Twitter Tool](http://mike.verdone.ca/twitter/) and [Twitter Streaming API](https://dev.twitter.com/docs/api/streaming) and inspired by [EarthQuake](https://github.com/jugyo/earthquake)

## Screenshot
![v0.0.1](https://raw.githubusercontent.com/DTVD/rainbowstream/master/screenshot/RainbowStreamv0.0.1.png)

## Install
**The recommened way:**
* Clone this repo
* Create virtualenv (optional but recommended)
* Install dependencies
* Install the package itself

```bash
git clone https://github.com/DTVD/rainbowstream.git
cd rainbowstream
virtualenv venv # Assume that you have virtualenv installed by "pip install virtualenv"
source venv/bin/activate
pip install -e .
```
**The quick way:**
* Install everything over the air

```bash
sudo pip install git+https://github.com/DTVD/rainbowstream.git
```
**Note the I only support Python version 2.7+**

## Usage
```bash
rainbowstream
```
In the first time you will be asked for authorization of Rainbow Stream app at Twitter.
Just click the "Authorize access" button and paste PIN number to the terminal, the rainbow will start.

While the rainbow stream is continued, you can search, list follower, following user, tweet directly from console, etc...
Type 'h' to view help or see screenshot above.

## License
Rainbow Stream are released under an MIT License. See LICENSE.txt for details
