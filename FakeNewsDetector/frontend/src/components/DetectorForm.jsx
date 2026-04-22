import { useState } from 'react';
import axios from 'axios';
import { Search, Loader2, ShieldCheck, AlertTriangle } from 'lucide-react';

export default function DetectorForm() {
  const [text, setText] = useState('');
  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  const analyzeText = async (e) => {
    e.preventDefault();
    if (!text.trim()) return;

    setLoading(true);
    setError('');
    setResult(null);

    try {
      const response = await axios.post('http://localhost:5000/predict', { text });
      setResult(response.data);
    } catch (err) {
      setError(err.response?.data?.error || 'Failed to connect to the AI model.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="glass-panel">
      <div className="header">
        <h1>AI Truth Engine</h1>
        <p>Detect fake news using advanced Machine Learning</p>
      </div>

      <form onSubmit={analyzeText}>
        <div className="input-group">
          <textarea
            value={text}
            onChange={(e) => setText(e.target.value)}
            placeholder="Paste a news headline or article here..."
            rows={5}
          />
        </div>
        <button type="submit" disabled={loading || !text.trim()}>
          {loading ? (
            <><Loader2 className="spinner" size={20} /> Analyzing...</>
          ) : (
            <><Search size={20} /> Detect Fake News</>
          )}
        </button>
      </form>

      {error && <div className="error-message">{error}</div>}

      {result && (
        <div className={`result-card ${result.prediction === 'Real News' ? 'real' : 'fake'}`}>
          <div className="result-header">
            {result.prediction === 'Real News' ? (
              <ShieldCheck size={32} className="icon-real" />
            ) : (
              <AlertTriangle size={32} className="icon-fake" />
            )}
            <h2>{result.prediction}</h2>
          </div>
          
          <div className="confidence-meter">
            <div className="confidence-info">
              <span>AI Confidence</span>
              <span>{result.confidence}%</span>
            </div>
            <div className="progress-bar-bg">
              <div 
                className="progress-bar-fill" 
                style={{ width: `${result.confidence}%` }}
              ></div>
            </div>
          </div>

          <div className="explanation">
            <strong>{result.explanation}</strong>
          </div>
        </div>
      )}
    </div>
  );
}
