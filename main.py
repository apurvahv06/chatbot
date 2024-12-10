import logging
import re
from flask import Flask, request, jsonify
from flask_cors import CORS
import nltk
from nltk.tokenize import word_tokenize
from difflib import SequenceMatcher
import spellchecker

nltk.download('punkt')


app = Flask(__name__)
CORS(app)


# Configure detailed logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(levelname)s: %(message)s',
    filename='chatbot_debug.log'  # Log to a file
)

# Add logging statements in key functions
def chatbot_response(message):
    logging.debug(f"Received message: {message}")

spell = spellchecker.SpellChecker()

drone_catalog = [
    {
        "id": 1,
        "name": "HAWK 2.O",
        "price": 14999,
        "load capacity": "50 kg",
        "flightTime": "1 hr 20 min",
        "cameraResolution": 8,
        "maxSpeed": "26 m/s",
        "weight": "8 kg",
        "range": "120 km",
        "bestFor": "City Surveillance"
    },
    {
        "id": 2,
        "name": "VIRAJ 2.O",
        "price": 500000,
        "load capacity": "16 kg",
        "flightTime": "40 min",
        "cameraResolution": 8,
        "maxSpeed": "12 m/s",
        "weight": "24 kg",
        "range": "1.5 km",
        "bestFor": "perfect for firefighting and emergency operations"
    },
    {
        "id": 3,
        "name": "VIRAJ 1.O",
        "price": 450000,
        "load capacity": "10 kg",
        "flightTime": "18-21 min",
        "cameraResolution": 4,
        "maxSpeed": "8 m/s",
        "weight": "14 kg" ,
        "range": "5 km" ,
        "bestFor": "Seamless real-time data and video feeds"
    }
]

keyword_responses = {
   
    "drone types": "We offer various types of drones: Agriculture drones, Photography drones, Survey and Inspection drones and Nano drones. Each type is designed for specific use cases and skill levels.",
    "drone models": "Our models include the Phantom, Mavic, and Inspire series. The Phantom series is great for aerial photography, Mavic for portability, and Inspire for professional cinematography.",
    "best drones": "Some of the best drones we offer are the HAWK 2.O 2 and VIRAJ 2.O. The HAWK 2.0 drone takes city surveillance to the next level with a massive 50 kg load capacity and a range of 120 km. It offers a flying time of 1 hour 20 minutes and operates on 80 MHz and 1.4 GHz frequencies. Powered by a 12V/2A transmitter, it ensures a 70 km transmission distance and can reach speeds of up to 26 m/s. Weighing just 8 kg without payload, this drone combines powerful performance with lightweight design, making it perfect for large-scale surveillance operations, while the VIRAJ 2.0 firefighter drone features an impressive 16 kg load capacity and a flying distance of 1.5 km, making it perfect for firefighting and emergency operations. With a longer flight time of up to 40 minutes, it can cover large areas efficiently. The drone operates on a 2.4 GHz frequency, powered by a 12V/2A transmitter, ensuring stable communication and transmission. It offers a 1.5 km transmission and video signal range, with a maximum speed retention capability of 12 m/s. Weighing 24 kg without payload, it is designed for heavy-duty tasks.",
    "camera quality": "Our drones feature high-quality cameras with resolutions ranging from 1080p to 4K. The Mavic series, in particular, offers exceptional image stabilization and color accuracy.",
    "drone features": "Key features include GPS positioning, obstacle avoidance, intelligent flight modes, follow-me tracking, automated return-to-home, and advanced camera stabilization.",
    "beginner drones": "For beginners, we recommend the VIRAJ 1.O. The drone is lightweight, easy to control, and come with beginner-friendly features like altitude hold and simple controls.",
    "advanced drones": "Professional users will love our VIRAJ 2.O. The drone offer advanced features like professional-grade camera systems, longer flight times, and sophisticated obstacle avoidance.",
    "flight range": "Flight range varies by model. The HAWK 2.O offers up to 120 km of range with HD video transmission, while the VIRAJ 2.O Pro can reach up to 1.5 km.",
    "GPS drones": "Most of our drones come with advanced GPS systems that enable features like precise hovering, automated waypoint navigation, and safe return-to-home functionality.",
    "autopilot": "Our advanced drones feature sophisticated autopilot capabilities. These include automated flight paths, point of interest orbits, and intelligent tracking modes.",
    
    
    "affordable drones": "Budget-conscious drone enthusiasts can find great options starting from ₹10,000. The DJI Mini 2 offers exceptional value at around ₹30,000.",
    "cheap drones": "We have budget-friendly options like the Ryze Tello at ₹10,000, perfect for beginners and indoor flying.",
    "best deals": "Watch out for our seasonal sales, especially during festive periods. We offer significant discounts on selected models.",
    "price range": "Our drones range from entry-level models at ₹10,000 to professional-grade drones at ₹1,50,000. We have options for every budget and skill level.",
    "cost of drone cameras": "Camera-equipped drones range from ₹30,000 for basic models to ₹1,20,000 for professional cinematography drones.",
    "discount code": "Use 'DRONE20' for a 20% discount on your first purchase. Terms and conditions apply.",
    
    
    "delivery time": "Standard delivery takes 3-7 business days. Expedited shipping is available for urgent requirements.",
    "shipping charges": "Shipping costs depend on your location and selected shipping method. Free shipping for orders above ₹10,000.",
    "free shipping": "Orders over ₹10,000 qualify for free standard shipping across India.",
    "eligibility return": "Items must be returned within 5 days of the delivery date. : Items must be unused and in the same condition that you received them. :Items must be in the original packaging.: A receipt or proof of purchase is required for all returns.",
    "return process": "Initiate a Return: Contact our customer support team at [customer support email] with your order number and reason for the return. : Return Authorization: Once your return request is approved, you will receive a Return Merchandise Authorization (RMA) number and return instructions. :Ship the Item: Pack the item securely and include your RMA number. Ship the item to the address provided in the return instructions. :Inspection: Upon receiving the returned item, we will inspect it to ensure it meets the return conditions."
    "refund eligibility" "1. Refunds are issued to the original payment method. 2. Shipping costs are non-refundable. 3.Refunds will be processed within 7-10 business days after we receive and inspect the returned item.",
    "exchange": "We only replace items if they are defective or damaged. If you need to exchange an item, contact our customer support team at [customer support email] with your order number and details of the issue.",

    "Order Processing": "Orders are processed within 2-3 business days (excluding weekends and holidays) after receiving your order confirmation email. You will receive another notification when your order has shipped.",
    "Order Cutoff Time": "Orders placed after 3 PM (local time) will be processed the next business day.",
    "Shipping Confirmation Order Tracking":"Once your order has shipped, you will receive a shipping confirmation email with a tracking number. You can track your order using the link provided in the email.",
    "damange": "Drone Planet is not liable for any products damaged or lost during shipping. If you received your order damaged, please contact the shipment carrier to file a claim. Save all packaging materials and damaged goods before filing a claim.",

    
    "drone laws": "Drone usage is regulated by the DGCA. Drones over 250g must be registered. Always check local regulations before flying.",
    "drone registration": "To register a drone, visit the DGCA website. You'll need proof of purchase and identification documents.",


    "drone battery life": "Battery life varies by model:\n- Entry-level drones: 10-15 minutes\n- Mid-range drones: 20-30 minutes\n- Professional drones: 30-45 minutes\nTip: Always carry spare batteries for extended flights!",
    "drone weight": "Drone weights:\n- Ultralight (under 250g): DJI Mini 2\n- Lightweight (250g-500g): Most beginner drones\n- Mid-weight (500g-2kg): Professional photography drones\n- Heavy (2kg+): Industrial and specialized drones",
    "drone camera specs": "Camera specifications:\n- Entry-level: 720p-1080p resolution\n- Mid-range: 2.7K resolution\n- Professional: 4K resolution with advanced stabilization\n- Special features: Gimbal stabilization, RAW photo capture, HDR",
    "drone range": "Flight ranges by model:\n- Beginner drones: 50-100 meters\n- Mid-range drones: 1-5 kilometers\n- Professional drones: Up to 10 kilometers\nAlways check local regulations for maximum allowed range.",


    "spare parts": "Spare parts availability:\n- Propellers\n- Batteries\n- Cameras\n- Gimbals\n- Motors\n- Spare controllers",
    "drone hire": "We offer drone rental services for events, photography, and professional surveys. Contact our sales team for custom quotes.",
    "drone photography": "Our professional drone photography services cover weddings, real estate, events, and aerial cinematography.",
    "drone survey": "We provide aerial surveying for construction, agriculture, land mapping, and infrastructure inspection.",
    

    "about us": "Drone Planet is your ultimate platform for all things drones! From training and job opportunities, buying and selling to advanced aerial solutions, we're empowering the drone community to soar to new height.",
    "company information": "Based in Gurugram  , we're committed to providing cutting-edge drone technology and exceptional customer service.",
    "contact": "If you have any questions about this Shipping Policy or need assistance with your order, please contact our customer service team at support@droneplanet.in or call us at +91 9898765432.",
    
    "drone comparison": "I can help you compare drones! You can request a comparison by specifying two drone names, for example: 'VIRAJ 1.O and VIRAJ 2.O'.",
    "compare drones": "Sure, I can help you compare drones. Just tell me the names of the two drones you want to compare."
}

def compare_drones(drone1_name, drone2_name):
    """
    Compare two drones based on their names
    """
    # Find drones in the catalog
    drone1 = next((drone for drone in drone_catalog if drone1_name.lower() in drone['name'].lower()), None)
    drone2 = next((drone for drone in drone_catalog if drone2_name.lower() in drone['name'].lower()), None)
    
    # If either drone not found
    if not drone1 or not drone2:
        return "Sorry, I couldn't find one or both of the drones you want to compare."
    
    # Create comparison summary
    comparison = f"""Drone Comparison: {drone1['name']} vs {drone2['name']}
    
Price:
- {drone1['name']}: ₹{drone1['price']}
- {drone2['name']}: ₹{drone2['price']}

Flight Time:
- {drone1['name']}: {drone1['flightTime']} minutes
- {drone2['name']}: {drone2['flightTime']} minutes

Camera Resolution:
- {drone1['name']}: {drone1['cameraResolution']}K
- {drone2['name']}: {drone2['cameraResolution']}K

Max Speed:
- {drone1['name']}: {drone1['maxSpeed']} mph
- {drone2['name']}: {drone2['maxSpeed']} mph

Weight:
- {drone1['name']}: {drone1['weight']} kg
- {drone2['name']}: {drone2['weight']} kg

Range:
- {drone1['name']}: {drone1['range']} meters
- {drone2['name']}: {drone2['range']} meters

Best For:
- {drone1['name']}: {drone1['bestFor']}
- {drone2['name']}: {drone2['bestFor']}
    """
    
    return comparison

def chatbot_response(message):
    """
    Enhanced chatbot response to handle drone comparisons
    """
    processed_message = preprocess_message(message)
    logging.debug(f"Processed message: {processed_message}")
    
    # Check for comparison request
    comparison_keywords = ['compare', 'comparison', 'vs', 'versus']
    if any(keyword in processed_message for keyword in comparison_keywords):
        # Extract drone names
        words = processed_message.split()
        potential_drones = [
            word for word in words 
            if any(drone['name'].lower() in word.lower() for drone in drone_catalog)
        ]
        
        # If two drone names found, perform comparison
        if len(potential_drones) >= 2:
            return compare_drones(potential_drones[0], potential_drones[1])
        

def preprocess_message(message):
    
    message = message.lower()
    
    
    corrected_words = []
    for word in message.split():
        
        corrected_word = spell.correction(word)
        corrected_words.append(corrected_word)
    
    return ' '.join(corrected_words)

def find_best_keyword_match(message, keywords):
    """
    Find the best matching keyword using multiple strategies
    """
    
    if message in keywords:
        return message
    
    
    best_match = None
    best_score = 0
    
    for keyword in keywords:
        
        similarity = SequenceMatcher(None, message, keyword).ratio()
        
        
        word_matches = any(
            keyword_word in message or 
            message in keyword_word or 
            SequenceMatcher(None, keyword_word, message).ratio() > 0.7 
            for keyword_word in keyword.split()
        )
        
        
        score = similarity
        if word_matches:
            score += 0.2
        
        
        if score > best_score:
            best_score = score
            best_match = keyword
    
    
    return best_match if best_score > 0.6 else None

def chatbot_response(message):
    """
    Generate intelligent chatbot response with spelling error tolerance
    """
    
    processed_message = preprocess_message(message)
    logging.debug(f"Processed message: {processed_message}")
    
    
    best_match = find_best_keyword_match(processed_message, keyword_responses.keys())
    
    
    if best_match:
        logging.debug(f"Matched keyword: {best_match}")
        return keyword_responses[best_match]
    
    
    tokens = processed_message.split()
    for token in tokens:
        partial_matches = [
            keyword for keyword in keyword_responses.keys() 
            if token in keyword or any(token in word for word in keyword.split())
        ]
        
        if partial_matches:
            
            logging.debug(f"Partial match found: {partial_matches[0]}")
            return keyword_responses[partial_matches[0]]
    
    
    generic_responses = {
        "help": "I can help you with information about drones. Try asking about drone types, models, features, prices, or services.",
        "hello": "Hi there! Welcome to Drone Planet. How can I assist you today with drone-related queries?",
    }
    
    
    for phrase, response in generic_responses.items():
        if phrase in processed_message:
            return response
    
    
    return "I'm having trouble understanding your specific query. Could you please rephrase or ask about drones, their features, prices, or services?"


@app.route('/chat', methods=['POST'])
def chat():
    user_message = request.json.get('message')
    if not user_message:
        return jsonify({"error": "Message is required"}), 400

    bot_response = chatbot_response(user_message)
    return jsonify({"response": bot_response})

@app.route('/compare_drones', methods=['POST'])
def compare_drones_route():
    data = request.json
    drone1 = data.get('drone1')
    drone2 = data.get('drone2')
    
    if not drone1 or not drone2:
        return jsonify({"error": "Please provide two drone names"}), 400
    
    comparison_result = compare_drones(drone1, drone2)
    return jsonify({"comparison": comparison_result})

if __name__ == '__main__':
    app.run(debug=True)
