import './App.css';
import React, { useState } from 'react';
import axios from 'axios';

const backendUrlSend = "https://apolnav.pythonanywhere.com/get_gainz";

function App() {

  const [images, setImages] = useState<string[]>([]);
  const [loading, setLoading] = useState(false);

  const changeHandler = (event: React.ChangeEvent<HTMLInputElement>) => {
    if (!event.target.files) {
      return;
    }

    const file = event.target.files[0];
    const formData = new FormData();
    formData.append("file", file);
    setLoading(true);
    axios.post(backendUrlSend, formData, {
      headers: { "Content-Type": "multipart/form-data" }
    }).then(
      async result => {
        setImages(result.data);
        setLoading(false);
      }
    )
  };

  const Spinner = () => {
    return (
      <div className="spinner-container">
        <div className="spinner"></div>
      </div>
    );
  };

  return (
    <div>
      <input
        type="file"
        name="file"
        accept=".csv"
        onChange={changeHandler}
        style={{ display: "block", margin: "10px auto" }}
      />
      {loading ? (
        <Spinner />
      ) : (
        <div>
          {images.map((base64String, index) => (
            <img
              key={index}
              src={`data:image/png;base64,${base64String}`}
              alt={`Plot ${index + 1}`}
            />
          ))}
        </div>
      )}

    </div>
  );
}

export default App;
