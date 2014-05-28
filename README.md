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
#### The stream
Just type
```bash
rainbow
```
and see your stream.

In the first time you will be asked for authorization of Rainbow Stream app at Twitter.
Just click the "Authorize access" button and paste PIN number to the terminal, the rainbow will start.

#### The interactive mode
While the rainbow stream is continued, you are also ready to tweet, search, reply, retweet... directly from console.
Simply hit Enter key and type "h" to view the help

Input is in interactive mode. It means that you can use arrow key to move up and down history, tab-autocomplete or 2 tab to view available suggestion

Here is full list of supported command

```bash
[@dtvd88]home 
```
Show your timeline. A number come after will decide number of tweets to print. Ex 'home 10'.

```bash
[@dtvd88]view @mdo 
```
Show @mdo 's timeline.

```bash
[@dtvd88]t the rainbow is god's promise to noah
```
Tweet exactly 'the rainbow is god's promise to noah'

```bash
[@dtvd88]rt 1
```
Retweet the tweet with [id=1]. You can see id of each tweet beside the time.

```bash
[@dtvd88]rep 1 Really
```
Reply 'Really' to the tweet with [id=1].

```bash
[@dtvd88]del 1
```
Delete thw tweet with [id=1].

```bash
[@dtvd88]s #noah
```
Search the word 'noah'. Result will come back with highlight.

```bash
[@dtvd88]fr
```
List all friend (You are following people).

```bash
[@dtvd88]fl
```
List all follower.

```bash
[@dtvd88]h
```
SHow the help.

```bash
[@dtvd88]c
```
Clear the screen.


```bash
[@dtvd88]q
```
Quit.

For example see the screenshot above.

## Bug Report
Please [create an issue](https://github.com/DTVD/rainbowstream/issues/new) 
or contact me at [@dtvd88](https://twitter.com/dtvd88)

## License
Rainbow Stream are released under an MIT License. See LICENSE.txt for details
