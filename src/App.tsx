import './App.css';
import React, { useEffect, useState } from 'react';
import axios from 'axios';

const backendUrlSend = "http://127.0.0.1:5000/get_gainz";

function App() {

  const [images, setImages] = useState<string[]>([]);

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
        setImages(result.data);
      }
    )
  };


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
      {images.map((base64String, index) => (
        <img
          key={index}
          src={`data:image/png;base64,${base64String}`}
          alt={`Image ${index + 1}`}
        />
      ))}
    </div>
  );
}

export default App;
