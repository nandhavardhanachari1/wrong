import React, { useState, useEffect } from "react";
import axios from "axios";

function Challenge() {

  const [name,setName] = useState("");
  const [goal,setGoal] = useState("");
  const [days,setDays] = useState("");
  const [challenges,setChallenges] = useState([]);

  const API = "http://localhost:5000";

  useEffect(()=>{
    fetchChallenges();
  },[]);

  const fetchChallenges = async ()=>{
    const res = await axios.get(API + "/challenges");
    setChallenges(res.data);
  };

  const addChallenge = async ()=>{

    await axios.post(API + "/add",{
      name,
      goal,
      days,
      progress:0
    });

    setName("");
    setGoal("");
    setDays("");

    fetchChallenges();
  };

  return (
    <div style={{padding:"20px"}}>

      <h2>Fitness Challenge App</h2>

      <input
        placeholder="Challenge Name"
        value={name}
        onChange={(e)=>setName(e.target.value)}
      />

      <br/><br/>

      <input
        placeholder="Goal"
        value={goal}
        onChange={(e)=>setGoal(e.target.value)}
      />

      <br/><br/>

      <input
        placeholder="Days"
        value={days}
        onChange={(e)=>setDays(e.target.value)}
      />

      <br/><br/>

      <button onClick={addChallenge}>
        Add Challenge
      </button>

      <hr/>

      <h3>Challenges</h3>

      {challenges.map((c)=>(
        <div key={c._id} style={{border:"1px solid gray",padding:"10px",margin:"10px"}}>
          <h4>{c.name}</h4>
          <p>Goal: {c.goal}</p>
          <p>Days: {c.days}</p>
          <p>Progress: {c.progress}%</p>
        </div>
      ))}

    </div>
  );
}

export default Challenge;