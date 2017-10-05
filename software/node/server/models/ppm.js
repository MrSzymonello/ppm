var mongoose = require('mongoose');

var PPM = mongoose.model('PPM', {
  b: {
    type: Number,
    required: true
  },
  fitFrequency: {
	  type: Number,
    required: true
  },
  fftFrequency: {
	  type: Number,
    required: true
  },
  fftAmplitude: {
	  type: Number,
    required: true
  },
  t0: {
	  type: Number,
    required: true
  },
  A: {
	  type: Number,
    required: true
  },
  x0Error: {
	  type: Number,
    required: true
  },
  fError: {
	  type: Number,
    required: true
  },
  t0Error: {
	  type: Number,
    required: true
  },
  AError: {
	  type: Number,
    required: true
  },
  y0Error: {
	  type: Number,
    required: true
  },
  takenAt: {
    type: Number,
    required: true
  },
  sampleRate: {
    type: Number,
    required: true
  },
  numberOfSamples: {
    type: Number,
    required: true
  }
});

module.exports = {PPM};
