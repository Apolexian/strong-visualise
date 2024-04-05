import './App.css';
import React, { useState } from 'react';
import axios from 'axios';
import { FaGithub } from 'react-icons/fa';

const backendUrlSend = "https://apolnav.pythonanywhere.com/get_gainz";

interface FileInputProps {
  label: string;
  onFileChange: (event: React.ChangeEvent<HTMLInputElement>) => void;
}

const FileInput: React.FC<FileInputProps> = ({ label, onFileChange }) => {
  const handleFileChange = (event: React.ChangeEvent<HTMLInputElement>) => {
    if (event.target.files && event.target.files[0]) {
      onFileChange(event);
    }
  };

  return (
    <div className="file-input-container"> {/* Apply CSS class for styling */}
      <label>{label}</label>
      <input type="file" onChange={handleFileChange} />
    </div>
  );
};

const Footer = () => {
  return (
    <footer className="footer">
      <p className="footer-text">Consider contributing to the project</p>
      <a
        href="https://github.com/Apolexian/strong-visualise"
        target="_blank"
        rel="noopener noreferrer"
        className="github-link"
      >
        <FaGithub className="github-icon" />
      </a>
    </footer>
  );
};


const Explanation: React.FC = () => {
  return (
    <div className="explanation-container">
      <p style={{
        textAlign: 'center',
        color: '#fff',
        marginTop: '50px',
        fontFamily: 'Arial, sans-serif',
        fontSize: '36px',
        fontWeight: 'bold',
        textTransform: 'uppercase',
        letterSpacing: '2px',
        textShadow: '2px 2px 4px rgba(0, 0, 0, 0.3)'
      }}>
        Input the data you exported from the Strong app. Better explanation coming soon.
      </p>
    </div>
  );
};

const Heading: React.FC = () => {
  return (
    <h1 style={{
      textAlign: 'center',
      color: '#fff',
      marginTop: '50px',
      fontFamily: 'Arial, sans-serif',
      fontSize: '36px',
      fontWeight: 'bold',
      textTransform: 'uppercase',
      letterSpacing: '2px',
      textShadow: '2px 2px 4px rgba(0, 0, 0, 0.3)'
    }}>
      Visualize your strong data
    </h1>
  );
};

function App() {

  const [images, setImages] = useState<string[]>([]);
  const [loading, setLoading] = useState(false);
  const [file1, setFile1] = useState<File | null>(null);
  const [file2, setFile2] = useState<File | null>(null);
  const [submitDisabled, setSubmitDisabled] = useState<boolean>(true);
  const [buttonPressed, setButtonPressed] = useState<boolean>(false);
  const [errorMessageFile1, setErrorMessageFile1] = useState('');
  const [errorMessageFile2, setErrorMessageFile2] = useState('');

  const handleFile1Change = (event: React.ChangeEvent<HTMLInputElement>) => {
    const files = event.target.files;
    if (!files || files.length === 0) {
      return;
    }
    const file = files[0];
    const fileType = file.type;
    const validFileTypes = ['text/csv'];

    if (!validFileTypes.includes(fileType)) {
      setErrorMessageFile1('Please select a CSV file.');
      event.target.value = '';
      return;
    }

    setErrorMessageFile1('');
    setFile1(file);
  };

  const handleFile2Change = (event: React.ChangeEvent<HTMLInputElement>) => {
    const files = event.target.files;
    if (!files || files.length === 0) {
      return;
    }
    const file = files[0];
    const fileType = file.type;
    const validFileTypes = ['text/csv'];

    if (!validFileTypes.includes(fileType)) {
      setErrorMessageFile2('Please select a CSV file.');
      event.target.value = '';
      return;
    }

    setErrorMessageFile2('');
    setFile2(file);
  };

  const handleSubmit = () => {
    setButtonPressed(true);
    if (file1 && file2) {
      const file = file1;
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
    } else {
      // Handle the case where one or both files are null
      console.error("Error: Both files must be selected.");
    }
  };

  React.useEffect(() => {
    if (file1 && file2) {
      setSubmitDisabled(false);
    } else {
      setSubmitDisabled(true);
    }
  }, [file1, file2]);

  const Spinner = () => {
    return (
      <div className="spinner-container">
        <div className="spinner"></div>
      </div>
    );
  };

  return (
    <div>
      <Heading />
      {(!buttonPressed) ? (
        <div className="content-container">
          <div className="file-upload-container"> {/* Apply CSS class for centering and top margin */}
            {!buttonPressed && (
              <div className="form-container"> {/* Apply CSS class for styling */}
                <div className="file-inputs-container"> {/* Separate container for file inputs */}
                  <FileInput label="Your data" onFileChange={handleFile1Change} />
                  {errorMessageFile1 && <p style={{ color: 'red' }}>{errorMessageFile1}</p>}
                  {file1 && (
                    <div>
                      <FileInput label="Your second data" onFileChange={handleFile2Change} />
                      {errorMessageFile2 && <p style={{ color: 'red' }}>{errorMessageFile2}</p>}
                    </div>
                  )}
                </div>
                <div className="button-container"> {/* Separate container for the button */}
                  {file2 && (
                    <button onClick={handleSubmit} disabled={submitDisabled}>
                      Submit
                    </button>
                  )}
                </div>

              </div>
            )}
          </div>
          {<Explanation />}
        </div>
      ) : (
        <div>
          {(loading) ? (
            <Spinner />
          ) : (
            <div className="image-gallery-container">
              {images.map((base64String, index) => (
                <img
                  className="gallery-image"
                  key={index}
                  src={`data:image/png;base64,${base64String}`}
                  alt={`Plot ${index + 1}`}
                />
              ))}
            </div>
          )}
        </div>
      )};
      <Footer />
    </div>

  )
}

export default App;
