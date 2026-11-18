const express = require("express");
const mongoose = require("mongoose");
const cors = require("cors");

const app = express();

app.use(cors());
app.use(express.json());

// MongoDB Connection
mongoose.connect("mongodb://127.0.0.1:27017/mernDB")
  .then(() => console.log("MongoDB Connected"))
  .catch((err) => console.log(err));

// Import Student Model
const Student = require("./models/Student");

// Test Route
app.get("/", (req, res) => {
  res.send("Student API Running...");
});

// Save Student (ONLY SAVE — NO LIST)
app.post("/api/students", async (req, res) => {
  try {
    const { name, email, age, course } = req.body;

    const newStudent = new Student({
      name,
      email,
      age,
      course
    });

    await newStudent.save();

    res.status(201).json({ message: "Student Saved Successfully" });

  } catch (error) {
    res.status(500).json({ error: error.message });
  }
});

const PORT = 5000;

app.listen(PORT, () => {
  console.log(`Server running on port ${PORT}`);
});