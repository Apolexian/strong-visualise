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

const ErrorPopup: React.FC<ErrorPopupProps> = ({ message }) => {
  const closeError = () => {
    window.location.reload();
  };
  return (
    <div className="error-popup">
      <div className="error-popup-content">
        <span className="close" onClick={closeError}>&times;</span>
        <p>{message}</p>
      </div>
    </div>
  );
};

interface ErrorPopupProps {
  message: string
};

const Footer = () => {
  return (
    <footer className="footer">
      <p className="footer-text">Consider contributing to the project.</p>
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
        textAlign: 'left',
        color: '#fff',
        marginTop: '30px',
        fontFamily: 'Arial, sans-serif',
        fontSize: '17px',
        fontWeight: 'bold',
        textTransform: 'uppercase',
        letterSpacing: '1px',
        textShadow: '2px 2px 4px rgba(0, 0, 0, 0.3)',
      }}>
        <ol>
          <li>
            Follow the Strong App <a href="https://help.strongapp.io/article/235-export-workout-data">instructions on exporting your data</a>.
          </li>
          <li>
            <p>Select this file for the first input.</p>
          </li>
          <li>
            <p>Create an Exercise Bank csv in the following format:</p>
            <img src="/Exercise_Bank.png" alt="The exercise bank consists of the Exercise Name, Primary Muscle Group, Secondary Muscle Group, MRV, MEV and MAV(P) columns."></img>
            <p><a href="/exercises.csv" download>Download the example Exercise Bank to edit</a></p>
          </li>
          <li>
            <p>Use the Exercise Bank CSV as the second input.</p>
          </li>
          <li><p>Hit Go.</p></li>
        </ol>

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
  const [errorPopUp, setErrorPopUp] = useState<boolean>(false);
  const [errorPopUpMessage, setErrorPopUpMessage] = useState('');

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
      ).catch(function (error) {
        setLoading(false);
        setErrorPopUp(true);
        setErrorPopUpMessage(`An error has occurred: ${error.response.data.error}`);
      });
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
                  <FileInput label="Your Strong App data" onFileChange={handleFile1Change} />
                  {errorMessageFile1 && <p style={{ color: 'red' }}>{errorMessageFile1}</p>}
                  {file1 && (
                    <div>
                      <FileInput label="Your Exercise Bank" onFileChange={handleFile2Change} />
                      {errorMessageFile2 && <p style={{ color: 'red' }}>{errorMessageFile2}</p>}
                    </div>
                  )}
                </div>
                <div className="button-container"> {/* Separate container for the button */}
                  {file2 && (
                    <button onClick={handleSubmit} disabled={submitDisabled}>
                      Go
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
            <div>
              {(errorPopUp) ? (
                <ErrorPopup message={errorPopUpMessage} />) : (
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

          )}
        </div>
      )};
      <Footer />
    </div>

  )
}

export default App;
