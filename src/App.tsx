import './App.css';
import React, { useEffect, useState } from 'react';
import axios from 'axios';


type StrongData = {
  Date: string,
  WorkoutName: string,
  ExerciseName: string
}

const backendUrlSend = "http://127.0.0.1:5000/get_gainz";

function App() {

  const [fileState, setFileState] = useState<File[]>()

  const changeHandler = (event: React.ChangeEvent<HTMLInputElement>) => {
    if (!event.target.files) {
      return;
    }

    const file = event.target.files[0];
    const formData = new FormData();
    formData.append("file", file);

    axios.post(backendUrlSend, formData, {
      headers: { "Content-Type": "multipart/form-data" }
    }).then(
      async result => {
        
      }
    )
  };

  useEffect(() => {
    console.log(fileState, '- Has changed')
  }, [fileState]) // <-- here put the parameter to listen, react will re-render component when your state will be changed


  return (
    <div>
      {/* File Uploader */}
      <input
        type="file"
        name="file"
        accept=".csv"
        onChange={changeHandler}
        style={{ display: "block", margin: "10px auto" }}
      />
    </div>
  );
}

export default App;
