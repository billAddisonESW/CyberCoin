# Learn Blockchains by Building One

This is the source code for Daniel van Flymen's Hackernoon post on [Building a Blockchain](https://medium.com/p/117428612f46).

Adapted by [Ben Galloway](mailto:ben@bengalloway.io) for use at UAE Cyber Quest 2018, including the addition of a simple webapp frontend (here contained in the `static` directory) served as static files by Flask.

## Installation

[Download this branch](https://github.com/bengal75/cyberquest-blockchain-api/archive/package.zip) of this repository, and extract the zip file. In a command window, in the same directory as this file, run the following steps. Only steps 2 and 3 require an internet connection.

1. Check that Python is available. The Hackernoon code requires Python 3, so it's probably easiest to use that binary explicitly:
```bash
python3 --version
```
2. The easiest way to get the dependencies right is to install the pip3 package:
```bash
sudo apt-get install python3-pip
```
and then you should get some sensible output from:
```bash
pip3 --version
```
3. All being well, install the required Python dependencies:
```bash
pip3 install -r requirements.txt
```
4. Find out the LAN IP address of the laptop you're running on e.g. by running `ifconfig`. Edit the file `static/config.js` to reflect this. There are further instructions within that file, but if the IP address was, for example, 192.168.0.5, you would edit the relevant line in `config.js` to read exactly
```javascript
window.api="http://192.168.0.5";
```
5. Start the server by saying:
```bash
python3 blockchain.py
```
This will listen on port 80 by default, so all that the participants then need to do is connect to the IP address of the laptop that the Python script is running on, in a web browser - e.g. visit http://192.168.0.5

(There are nice things that we could do in the local hosts file on each participant laptop (or maybe on the workshop's router) to make this a bit prettier, but that's very much a nice-to-have rather than a necessity.)

6. The blockchain can be reset back to its initial state by visiting e.g. http://192.168.0.5/reset in a browser, where 192.168.0.5 is the IP address of the laptop running the Python script. As the script will say, it can also be terminated completely by pressing `Ctrl+C`, or just closing the terminal window.

# Additional Note (Kali Linux)
If it doesn't run, you may be running apache2 in the background. Stop it with:
```bash
sudo service apache2 stop
```