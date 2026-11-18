import { useEffect, useState } from "react"
import axios from "axios"

function App(){

const [challenges,setChallenges] = useState([])
const [name,setName] = useState("")
const [goal,setGoal] = useState("")
const [days,setDays] = useState("")

const fetchChallenges = async ()=>{
const res = await axios.get("http://localhost:5000/challenges")
setChallenges(res.data)
}

useEffect(()=>{
fetchChallenges()
},[])

const addChallenge = async()=>{
await axios.post("http://localhost:5000/challenges",{
name,
goal,
days
})

setName("")
setGoal("")
setDays("")
fetchChallenges()
}

const deleteChallenge = async(id)=>{
await axios.delete(`http://localhost:5000/challenges/${id}`)
fetchChallenges()
}

return(

<div className="min-h-screen bg-gradient-to-r from-indigo-500 via-purple-500 to-pink-500">

{/* Navbar */}

<div className="bg-black/20 backdrop-blur text-white p-4 shadow">

<div className="max-w-6xl mx-auto flex justify-between">

<h1 className="text-2xl font-bold">
🏋️ Fitness Challenge Tracker
</h1>

<p className="hidden md:block">
Stay Consistent 💪
</p>

</div>

</div>


<div className="max-w-6xl mx-auto p-6">

{/* Add Challenge */}

<div className="bg-white rounded-xl shadow-lg p-6 mb-10">

<h2 className="text-xl font-bold mb-4">
Add New Challenge
</h2>

<div className="grid md:grid-cols-3 gap-4">

<input
className="border p-3 rounded"
placeholder="Challenge Name"
value={name}
onChange={(e)=>setName(e.target.value)}
/>

<input
className="border p-3 rounded"
placeholder="Goal"
value={goal}
onChange={(e)=>setGoal(e.target.value)}
/>

<input
className="border p-3 rounded"
placeholder="Days"
value={days}
onChange={(e)=>setDays(e.target.value)}
/>

</div>

<button
onClick={addChallenge}
className="mt-4 bg-indigo-600 hover:bg-indigo-700 text-white px-6 py-2 rounded"
>
Add Challenge
</button>

</div>


{/* Challenge Cards */}

<div className="grid md:grid-cols-3 sm:grid-cols-2 gap-6">

{challenges.map((c)=>{

return(

<div
key={c._id}
className="bg-white p-6 rounded-xl shadow hover:shadow-2xl transition"
>

<h3 className="text-lg font-bold text-indigo-600">
{c.name}
</h3>

<p className="text-gray-600 mt-2">
Goal: {c.goal}
</p>

<p className="text-gray-600">
Days: {c.days}
</p>

{/* Progress bar */}

<div className="w-full bg-gray-200 h-3 rounded mt-4">

<div
className="bg-gradient-to-r from-green-400 to-green-600 h-3 rounded"
style={{width:`${c.progress}%`}}
></div>

</div>

<p className="text-sm mt-2">
Progress: {c.progress}%
</p>

<button
onClick={()=>deleteChallenge(c._id)}
className="mt-4 bg-red-500 hover:bg-red-600 text-white px-3 py-1 rounded"
>
Delete
</button>

</div>

)

})}

</div>

</div>

</div>

)

}

export default App