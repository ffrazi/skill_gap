import React, { useState } from 'react';
import axios from 'axios';
import './App.css';

function App() {
    const [resumeFile, setResumeFile] = useState(null);
    const [jdText, setJdText] = useState('');
    const [analysis, setAnalysis] = useState(null);
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState('');

    const handleFileChange = (e) => {
        setResumeFile(e.target.files[0]);
    };

    const handleSubmit = async (e) => {
        e.preventDefault();
        if (!resumeFile || !jdText) {
            setError('Please provide both a resume file and a job description.');
            return;
        }

        const formData = new FormData();
        formData.append('resume', resumeFile);
        formData.append('jd', jdText);

        setLoading(true);
        setError('');
        setAnalysis(null);

        try {
            const response = await axios.post('http://127.0.0.1:5000/api/analyze', formData, {
                headers: {
                    'Content-Type': 'multipart/form-data',
                },
            });
            setAnalysis(response.data);
        } catch (err) {
            setError(err.response?.data?.error || 'An unexpected error occurred.');
        }
        setLoading(false);
    };

    return (
        <div className="App">
            <header>
                <h1>PathUp: Resume Analyzer</h1>
                <p>Upload your resume and paste a job description to find your skill gaps.</p>
            </header>

            <form onSubmit={handleSubmit} className="form-container">
                <div>
                    <label htmlFor="resume">Upload Resume (PDF, PNG, JPG):</label>
                    <input type="file" id="resume" accept=".pdf,.png,.jpg,.jpeg" onChange={handleFileChange} />
                </div>
                <textarea
                    placeholder="Paste the job description here..."
                    value={jdText}
                    onChange={(e) => setJdText(e.target.value)}
                />
                <button type="submit" disabled={loading}>
                    {loading ? 'Analyzing...' : 'Analyze'}
                </button>
            </form>

            {error && <div className="error">{error}</div>}
            {loading && <div className="loading">Analyzing your profile... this may take a moment.</div>}
            {analysis && <Results data={analysis} />}
        </div>
    );
}

function Results({ data }) {
    return (
        <div className="results-container">
            <div className="results-grid">
                <div className="skill-list resume-skills">
                    <h3>Skills Found in Your Resume</h3>
                    <ul>
                        {data.resume_skills.map(skill => <li key={skill}>{skill}</li>)}
                    </ul>
                </div>
                <div className="skill-list jd-skills">
                    <h3>Skills Required by the Job</h3>
                    <ul>
                        {data.jd_skills.map(skill => <li key={skill}>{skill}</li>)}
                    </ul>
                </div>
            </div>

            {data.missing_skills.length > 0 && (
                <div className="skill-list gap-analysis">
                    <h3>Missing Skills</h3>
                     <ul>
                        {data.missing_skills.map(skill => <li key={skill}>{skill}</li>)}
                    </ul>
                </div>
            )}

            {data.recommendations.length > 0 && (
                <div className="skill-list recommendations">
                    <h3>Recommended Courses to Bridge the Gap</h3>
                    <ul>
                        {data.recommendations.map((rec, index) => (
                            <li key={index}>
                                <a href={rec.url} target="_blank" rel="noopener noreferrer">
                                    {rec.title}
                                </a>
                            </li>
                        ))}
                    </ul>
                </div>
            )}
        </div>
    );
}

export default App;
