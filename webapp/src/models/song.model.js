import mongoose from 'mongoose';
const { Schema } = mongoose;

const songSchema = new Schema({
    title: String,
    duration: Number,
    tempoStart: Number,
    maxStartLength: Number,
    tempoEnd: Number,
    maxEndLength: Number,
    owner: String
})