import mongoose from 'mongoose';
const { Schema } = mongoose;

const mixSchema = new Schema({
    title: String,
    duration: Number,
    tempoStart: Number,
    maxStartLength: Number,
    tempoEnd: Number,
    maxEndLength: Number,
    owner: String,
    containsSongs: [{
        title: String
    }]
})

mixSchema.methods.findByOwner = function(cb) {
    return mongoose.model("Mix").find({owner: this.owner}, cb)
}

