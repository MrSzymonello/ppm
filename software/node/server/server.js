require('./config/config');

const express = require('express');
const bodyParser = require('body-parser');
const http = require('http');
var PythonShell = require('python-shell');

var {mongoose} = require('./db/mongoose');
var {PPM} = require('./models/ppm');

var app = express();
const port = process.env.PORT;
var server = http.createServer(app);
app.use(bodyParser.json());

app.post('/ppms', (req, res) => {
  
  var ppm;

  // set request elements as arguments to the Python script
  var options = {
    args: [req.body.samplerate, req.body.takenAt, 'data', 'False']
  };

  var pyshell = new PythonShell('..\\python\\ppm_server.py', options);

  // send encoded samples to the Python script using stdin
  // too long to set it as an argument to the Python script
  pyshell.send(req.body.base64samples);

  // listen for ppm analysis results from the Python script
  // construct PPM object
  pyshell.on('message', function (message) {
    var split = message.split('\t');
    if(split[0] === "OK") {
        ppm = new PPM({
          b: parseFloat(split[1]),
          fitFrequency: parseFloat(split[2]),
          fftFrequency: parseFloat(split[3]),
          t0: parseFloat(split[4]),
          fftAmplitude: parseFloat(split[5]),
          A: parseFloat(split[6]),
          x0Error: parseFloat(split[7]),
          fError: parseFloat(split[8]),
          t0Error: parseFloat(split[9]),
          AError: parseFloat(split[10]),
          y0Error: parseFloat(split[11]),
          takenAt: req.body.takenAt,
          sampleRate: req.body.samplerate,
          numberOfSamples: parseInt(split[12])
        });
    }
  });

  // end the input stream and allow the process to exit 
  pyshell.end(function (err) {
    if(ppm != undefined) {
      ppm.save().then((doc) => {
        res.send(doc);
      }, (e) => {
        res.status(400).send(e);
      });
    } else {
      res.send("PPM analysis failed");
    }
  });
});

server.listen(port, () => {
  console.log(`Server is up on ${port}`);
});

module.exports = {app};
