import React, { useState } from 'react';
import './App.css';

function App() {
  // State to hold form data
  const [formData, setFormData] = useState({
    name: '',
    address: '',
    city: '',
    state: '',
    country: '',
    zip_code: '',
  });

  // State to hold the API response
  const [apiResponse, setApiResponse] = useState(null);

  // Function to update state on input change
  const handleInputChange = (e) => {
    const { id, value } = e.target;
    setFormData({ ...formData, [id]: value });
  };

  // Function to handle form submission
  const handleSubmit = async (e) => {
    e.preventDefault();
    try {
      const response = await fetch('http://127.0.0.1:5000/analyze_business', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(formData),
      });
      const data = await response.json();
      if (response.ok) {
        setApiResponse(data); // Update the state with the received data
      } else {
        alert("Error from API: ", data.error);
      }
    } catch (error) {
      alert('Error:', error);
    }
  };

  return (
    <div className="App">
      <header className="App-header">
        <form className='inputs' onSubmit={handleSubmit}>
          <label htmlFor="name">Name</label><br />
          <input type='text' id='name' value={formData.name} onChange={handleInputChange} required/><br />

          <label htmlFor="address">Address</label><br />
          <input type='text' id='address' value={formData.address} onChange={handleInputChange} required/><br />

          <label htmlFor="city">City</label><br />
          <input type='text' id='city' value={formData.city} onChange={handleInputChange} required/><br />

          <label htmlFor="state">State</label><br />
          <input type='text' id='state' value={formData.state} onChange={handleInputChange} required/><br />

          <label htmlFor="country">Country</label><br />
          <input type='text' id='country' value={formData.country} onChange={handleInputChange} required/><br />

          <label htmlFor="zip_code">Zip Code</label><br />
          <input type='text' id='zip_code' value={formData.zip_code} onChange={handleInputChange} required/><br />

          <button type='submit'>Submit</button>
        </form>

        {apiResponse && (
        <div className="api-response">
          <h2>API Response</h2>
          <p className="overall-score"><strong>Overall Score:</strong> {apiResponse.overall_score}</p>
          <h3>Reviews:</h3>
          <ul className="reviews-list">
            {apiResponse.reviews.map((review, index) => (
              <li key={index} className="review-item">
                <p><strong>Review:</strong> {review.review}</p>
                <p><strong>Aggregate Score:</strong> {review.aggregate_score}</p>
                <p><strong>Sentiment Score:</strong> {review.sentiment_score}</p>
                <p><strong>Subjectivity Score:</strong> {review.subjectivity_score}</p>
              </li>
            ))}
          </ul>
        </div>
      )}
    </header>
  </div>
  );
}

export default App;
