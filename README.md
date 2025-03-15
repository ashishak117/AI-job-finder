# AI-job-finder
AI page where it helps user to find there requirement matching Job details 
# AI Job Finder

AI Job Finder is an intelligent job recommendation system that matches your resume with real-time job listings. Built with a Flask backend and a React frontend, it fetches jobs from a free API, extracts text from your resume (PDF, DOCX, or TXT), and uses TF-IDF and cosine similarity to recommend the best job matches based on your skills and experience.

## Features
- **Resume Parsing**: Upload your resume in PDF, DOCX, or TXT format to extract skills and experience.
- **Job Fetching**: Pulls job listings from the Arbeitnow API with customizable filters (location, experience, job type).
- **AI Matching**: Uses TF-IDF and cosine similarity to rank jobs by relevance to your resume.
- **User-Friendly Interface**: A clean React frontend with Bootstrap styling and real-time feedback.
- **Error Handling**: Robust fallback mechanisms ensure you always get results, even if the API fails.

## Prerequisites
- **Python 3.8+**: For the Flask backend.
- **Node.js 16+**: For the React frontend.
- **Git**: To clone and manage the repository.

## Installation

### Backend Setup
1. **Clone the Repository**:
   ```bash
   git clone https://github.com/yourusername/ai-job-finder.git
   cd ai-job-finder/backend
