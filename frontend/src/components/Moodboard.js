import React, { useState } from 'react';
import axios from 'axios';
import './Moodboard.css';

const API_URL = 'http://localhost:8000';

function Moodboard() {
  const [layout, setLayout] = useState('4x4');
  const [selectedFiles, setSelectedFiles] = useState([]);
  const [loading, setLoading] = useState(false);
  const [generatedImage, setGeneratedImage] = useState(null);
  const [error, setError] = useState(null);

  const layoutOptions = [
    { value: '4x4', label: '4 Grid (2×2)' },
    { value: '8-grid', label: '8 Grid (2×4)' },
    { value: '16-grid', label: '16 Grid (4×4)' },
    { value: 'portrait-8', label: 'Portrait 8 Grid' },
    { value: 'portrait-16', label: 'Portrait 16 Grid' },
  ];

  const handleFileChange = (e) => {
    const files = Array.from(e.target.files);
    setSelectedFiles(files);
  };

  const handleGenerate = async () => {
    if (selectedFiles.length === 0) {
      setError('Please select at least one image');
      return;
    }

    setLoading(true);
    setError(null);
    setGeneratedImage(null);

    try {
      const formData = new FormData();
      formData.append('layout', layout);
      selectedFiles.forEach((file) => {
        formData.append('files', file);
      });

      const response = await axios.post(
        `${API_URL}/generate-moodboard`,
        formData,
        { headers: { 'Content-Type': 'multipart/form-data' } }
      );

      if (response.data.success) {
        setGeneratedImage(`${API_URL}${response.data.download_url}`);
      }
    } catch (err) {
      setError(err.response?.data?.detail || 'Failed to generate moodboard');
      console.error('Error:', err);
    } finally {
      setLoading(false);
    }
  };

  const handleDownload = () => {
    if (generatedImage) {
      const link = document.createElement('a');
      link.href = generatedImage;
      link.download = 'moodboard.png';
      link.click();
    }
  };

  const removeFile = (index) => {
    setSelectedFiles(selectedFiles.filter((_, i) => i !== index));
  };

  return (
    <div className="moodboard-container">
      <h2>Create Your Moodboard</h2>
      <div className="form-section">
        <div className="form-group">
          <label>Choose Layout</label>
          <select value={layout} onChange={(e) => setLayout(e.target.value)}>
            {layoutOptions.map((option) => (
              <option key={option.value} value={option.value}>
                {option.label}
              </option>
            ))}
          </select>
        </div>

        <div className="form-group">
          <label>Upload Images</label>
          <input type="file" accept="image/*" multiple onChange={handleFileChange} />
          <small>You can select multiple images at once</small>
        </div>

        {selectedFiles.length > 0 && (
          <div className="selected-files">
            <h4>Selected Images ({selectedFiles.length})</h4>
            <div className="file-list">
              {selectedFiles.map((file, index) => (
                <div key={index} className="file-item">
                  <span>{file.name}</span>
                  <button className="remove-btn" onClick={() => removeFile(index)}>
                    ✕
                  </button>
                </div>
              ))}
            </div>
          </div>
        )}

        <button className="generate-btn" onClick={handleGenerate} disabled={loading}>
          {loading ? 'Creating Moodboard...' : '✨ Generate Moodboard'}
        </button>
      </div>

      {error && <div className="error-message">❌ {error}</div>}

      {generatedImage && (
        <div className="result-section">
          <h3>Your Moodboard</h3>
          <img src={generatedImage} alt="Generated Moodboard" />
          <button className="download-btn" onClick={handleDownload}>
            ⬇️ Download Moodboard
          </button>
        </div>
      )}
    </div>
  );
}

export default Moodboard;