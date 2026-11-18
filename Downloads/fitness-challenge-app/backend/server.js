const express = require("express")
const mongoose = require("mongoose")
const cors = require("cors")

const app = express()

app.use(cors())
app.use(express.json())

mongoose.connect("mongodb+srv://nandha:nandha@cluster0.av62kvg.mongodb.net/?appName=Cluster0/fitnessDB")
.then(()=>console.log("MongoDB Connected"))
.catch(err=>console.log(err))

const ChallengeSchema = new mongoose.Schema({
    name:String,
    goal:String,
    days:Number,
    progress:{
        type:Number,
        default:0
    }
})

const Challenge = mongoose.model("Challenge",ChallengeSchema)

app.get("/challenges",async(req,res)=>{
    const data = await Challenge.find()
    res.json(data)
})

app.post("/challenges",async(req,res)=>{
    const newChallenge = new Challenge(req.body)
    await newChallenge.save()
    res.json(newChallenge)
})

app.delete("/challenges/:id",async(req,res)=>{
    await Challenge.findByIdAndDelete(req.params.id)
    res.json({message:"Deleted"})
})

const PORT = 5000

app.listen(PORT,()=>{
    console.log(`Server running on port ${PORT}`)
})