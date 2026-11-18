const mongoose = require("mongoose");

const ChallengeSchema = new mongoose.Schema({
    name: String,
    goal: String,
    days: Number,
    progress: {
        type: Number,
        default: 0
    }
});

module.exports = mongoose.model("Challenge", ChallengeSchema);