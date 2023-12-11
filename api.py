from flask import Flask, request, jsonify
import requests
import os
from dotenv import load_dotenv
from joblib import load
from textblob import TextBlob
from flask_cors import CORS

# Initialize Flask app
app = Flask(__name__)
CORS(app)

# Load the saved model and vectorizer 
model = load('\\Users\\Owner\\Desktop\\Stuff\\learn\\urban-eats\\LRM.joblib')
vectorizer = load('\\Users\\Owner\\Desktop\\Stuff\\learn\\urban-eats\\vectorizer.joblib')  # Update with the path to your saved vectorizer

# Load Yelp API key from .env file
load_dotenv()
yelp_api_key = os.getenv("YELP_API_KEY")

sentiment_mapping = {
    'Very Negative': -2,
    'Negative': -1,
    'Neutral': 0,
    'Positive': 1,
    'Very Positive': 2
}

def find_business(name, address, city, state, country, zip_code, yelp_api_key):
    """Find a business on Yelp using the provided details."""
    yelp_url = "https://api.yelp.com/v3/businesses/matches"
    headers = {'Authorization': f'Bearer {yelp_api_key}'}
    params = {
        "name": name,
        "address1": address,
        "city": city,
        "state": state,
        "country": country,
        "zip_code": zip_code,
        "match_threshold": "default"
    }

    response = requests.get(yelp_url, headers=headers, params=params)
    if response.status_code == 200:
        businesses = response.json().get('businesses', [])
        if businesses:
            return businesses[0]['id']
    return None

def get_reviews(business_id, yelp_api_key):
    """Get reviews for a business given its Yelp Business ID."""
    reviews_url = f"https://api.yelp.com/v3/businesses/{business_id}/reviews"
    headers = {'Authorization': f'Bearer {yelp_api_key}'}

    response = requests.get(reviews_url, headers=headers)
    if response.status_code == 200:
        return response.json().get('reviews', [])
    return []

def analyze_review_sentiment(review):
    """Analyze the sentiment of a review."""
    processed_text = vectorizer.transform([review])
    sentiment_label = model.predict(processed_text)[0]
    sentiment_score = sentiment_mapping.get(sentiment_label, 0)  # Default to 0 if label not found
    return sentiment_score

def calculate_aggregate_score(sentiment_score, subjectivity_score, star_rating=3):
    """Calculate the aggregate score for a review."""
    normalized_star_rating = star_rating - 3  # Normalize star rating to -2 to 2 scale
    weight = 1 - subjectivity_score if sentiment_score > 0 else 1
    return (sentiment_score * weight + normalized_star_rating) / 2

@app.route('/analyze_business', methods=['POST'])
def analyze_business():
    data = request.json
    name = data['name']
    address = data['address']
    city = data['city']
    state = data['state']
    country = data['country']
    zip_code = data['zip_code']

    business_id = find_business(name, address, city, state, country, zip_code, yelp_api_key)
    if business_id:
        yelp_reviews = get_reviews(business_id, yelp_api_key)
        analyzed_reviews = []

        for review_data in yelp_reviews:
            review_text = review_data['text']
            sentiment_score = analyze_review_sentiment(review_text)
            subjectivity_score = TextBlob(review_text).sentiment.subjectivity
            aggregate_score = calculate_aggregate_score(sentiment_score, subjectivity_score)

            analyzed_reviews.append({
                "review": review_text,
                "sentiment_score": sentiment_score,
                "subjectivity_score": subjectivity_score,
                "aggregate_score": aggregate_score
            })

        overall_score = sum(review['aggregate_score'] for review in analyzed_reviews) / len(analyzed_reviews)
        return jsonify({"overall_score": overall_score, "reviews": analyzed_reviews})

    else:
        return jsonify({"error": "Business not found"}), 404

if __name__ == '__main__':
    app.run(debug=True)
