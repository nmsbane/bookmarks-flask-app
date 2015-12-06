var urlToImage = require('url-to-image');
var url = process.argv[2]
var outfile = process.argv[3];

console.log(url);
console.log(outfile);

var options = {
    width: 1200,
    height: 800,
    // Give a short time to load additional resources
    requestTimeout: 100,
    clip_height: 800,
    verbose: false,
    phantomArguments: '--ignore-ssl-errors=true'
}

urlToImage(url, outfile, options)
  
  