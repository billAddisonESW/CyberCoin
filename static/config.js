// This must be changed for proper functioning in the workshop!
// Something like the IP address of the machine this
// is running on should do, e.g
// window.api = "http://192.168.0.5";
window.api = "https://api.blockchain.bengalloway.io";
// It must start with http:// and have no / at the end.

// There is an artificial delay introduced to the mining process
// (in addition to the time it naturally takes)
// to prevent participants from overloading the server.
// It can be adjusted here, in seconds.
window.mineDelay = 10; //seconds

// This determines how entered usernames are validated.
// (It probably doesn't need to be changed.)
// Currently this means:
// "letters and numbers only, at least one of!
// No spaces, no other (special) characters."
window.usernameRegexp = /^[\w]+$/;
