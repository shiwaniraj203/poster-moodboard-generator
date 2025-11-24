import React, { useState } from 'react';
import axios from 'axios';
import './QuotePoster.css';

const API_URL = 'http://localhost:8000';

function QuotePoster() {
  const [text, setText] = useState('');
  const [fontSize, setFontSize] = useState(50);
  const [color, setColor] = useState('#FFFFFF');
  const [alignment, setAlignment] = useState('center');
  const [orientation, setOrientation] = useState('horizontal');
  const [backgroundFile, setBackgroundFile] = useState(null);
  const [loading, setLoading] = useState(false);
  const [generatedImage, setGeneratedImage] = useState(null);
  const [error, setError] = useState(null);

  const handleFileChange = (e) => {
    if (e.target.files[0]) {
      setBackgroundFile(e.target.files[0]);
    }
  };

  const handleGenerate = async () => {
    if (!text.trim()) {
      setError('Please enter some text for your quote');
      return;
    }

    setLoading(true);
    setError(null);
    setGeneratedImage(null);

    try {
      const formData = new FormData();
      formData.append('text', text);
      formData.append('font_size', fontSize);
      formData.append('color', color);
      formData.append('alignment', alignment);
      formData.append('orientation', orientation);
      
      if (backgroundFile) {
        formData.append('background_file', backgroundFile);
      }

      const response = await axios.post(
        `${API_URL}/generate-quote-poster`,
        formData,
        { headers: { 'Content-Type': 'multipart/form-data' } }
      );

      if (response.data.success) {
        setGeneratedImage(`${API_URL}${response.data.download_url}`);
      }
    } catch (err) {
      setError(err.response?.data?.detail || 'Failed to generate poster');
      console.error('Error:', err);
    } finally {
      setLoading(false);
    }
  };

  const handleDownload = () => {
    if (generatedImage) {
      const link = document.createElement('a');
      link.href = generatedImage;
      link.download = 'quote-poster.png';
      link.click();
    }
  };

  return (
    <div className="quote-poster-container">
      <h2>Create Your Quote Poster</h2>
      <div className="form-section">
        <div className="form-group">
          <label>Your Quote or Text</label>
          <textarea
            value={text}
            onChange={(e) => setText(e.target.value)}
            placeholder="Enter your inspiring quote here..."
            rows="4"
          />
        </div>

        <div className="form-group">
          <label>Background Image (Optional)</label>
          <input type="file" accept="image/*" onChange={handleFileChange} />
          <small>Leave empty for default gradient background</small>
        </div>

        <div className="form-group">
          <label>Font Size: {fontSize}px</label>
          <input
            type="range"
            min="20"
            max="120"
            value={fontSize}
            onChange={(e) => setFontSize(Number(e.target.value))}
          />
        </div>

        <div className="form-group">
          <label>Text Color</label>
          <input type="color" value={color} onChange={(e) => setColor(e.target.value)} />
        </div>

        <div className="form-group">
          <label>Text Alignment</label>
          <select value={alignment} onChange={(e) => setAlignment(e.target.value)}>
            <option value="left">Left</option>
            <option value="center">Center</option>
            <option value="right">Right</option>
          </select>
        </div>

        <div className="form-group">
          <label>Orientation</label>
          <select value={orientation} onChange={(e) => setOrientation(e.target.value)}>
            <option value="horizontal">Horizontal</option>
            <option value="vertical">Vertical</option>
          </select>
        </div>

        <button className="generate-btn" onClick={handleGenerate} disabled={loading}>
          {loading ? 'Generating...' : '✨ Generate Poster'}
        </button>
      </div>

      {error && <div className="error-message">❌ {error}</div>}

      {generatedImage && (
        <div className="result-section">
          <h3>Your Generated Poster</h3>
          <img src={generatedImage} alt="Generated Poster" />
          <button className="download-btn" onClick={handleDownload}>
            ⬇️ Download Poster
          </button>
        </div>
      )}
    </div>
  );
}

export default QuotePoster;