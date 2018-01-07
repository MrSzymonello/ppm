var mongoose = require('mongoose');
var schema = new mongoose.Schema(
  {
    B: {
      type: Number,
      required: true
    },
    FitFrequency: {
      type: Number,
      required: true
    },
    FFTFrequency: {
      type: Number,
      required: true
    },
    FFTAmplitude: {
      type: Number,
      required: true
    },
    T0: {
      type: Number,
      required: true
    },
    A: {
      type: Number,
      required: true
    },
    X0Error: {
      type: Number,
      required: true
    },
    FError: {
      type: Number,
      required: true
    },
    T0Error: {
      type: Number,
      required: true
    },
    AError: {
      type: Number,
      required: true
    },
    Y0Error: {
      type: Number,
      required: true
    },
    TakenAt: {
      type: Number,
      required: true
    },
    SampleRate: {
      type: Number,
      required: true
    },
    NumberOfSamples: {
      type: Number,
      required: true
    }
  },
  { versionKey: false });
var PPM = mongoose.model('PPM', schema);

module.exports = {PPM};
