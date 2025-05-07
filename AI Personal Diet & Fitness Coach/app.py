from flask import Flask, render_template, request, jsonify, send_file
from datetime import datetime
import requests
import os
from gtts import gTTS
import json
from dotenv import load_dotenv

app = Flask(__name__)
load_dotenv()

# API Keys with fallback values
NUTRITIONIX_APP_ID = os.getenv('NUTRITIONIX_APP_ID', '')
NUTRITIONIX_APP_KEY = os.getenv('NUTRITIONIX_APP_KEY', '')
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY', '')

# Initialize OpenAI client only if API key is available
try:
    from openai import OpenAI
    client = OpenAI(api_key=OPENAI_API_KEY) if OPENAI_API_KEY else None
except ImportError:
    client = None

def calculate_bmr(weight, height, age, gender):
    """Calculate BMR using Mifflin-St Jeor Equation"""
    if gender.lower() == 'male':
        bmr = 10 * weight + 6.25 * height - 5 * age + 5
    else:
        bmr = 10 * weight + 6.25 * height - 5 * age - 161
    return bmr

def calculate_tdee(bmr, activity_level):
    """Calculate TDEE based on activity level"""
    activity_multipliers = {
        'sedentary': 1.2,
        'moderate': 1.55,
        'active': 1.725
    }
    return bmr * activity_multipliers.get(activity_level.lower(), 1.2)

def adjust_calories(tdee, goal):
    """Adjust calories based on fitness goal"""
    if goal.lower() == 'lose weight':
        return tdee - 500
    elif goal.lower() == 'gain muscle':
        return tdee + 500
    else:
        return tdee

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/calculate', methods=['POST'])
def calculate():
    data = request.json
    
    # Extract user data
    weight = float(data['weight'])
    height = float(data['height'])
    age = int(data['age'])
    gender = data['gender']
    activity_level = data['activity_level']
    goal = data['goal']
    diet_preference = data['diet_preference']
    
    # Calculate nutritional needs
    bmr = calculate_bmr(weight, height, age, gender)
    tdee = calculate_tdee(bmr, activity_level)
    target_calories = adjust_calories(tdee, goal)
    
    # Calculate macronutrient distribution
    protein = weight * 2.2  # 1g per pound of body weight
    fat = (target_calories * 0.25) / 9  # 25% of calories from fat
    carbs = (target_calories - (protein * 4 + fat * 9)) / 4  # Remaining calories from carbs
    
    # Prepare response
    response = {
        'bmr': round(bmr),
        'tdee': round(tdee),
        'target_calories': round(target_calories),
        'macros': {
            'protein': round(protein),
            'carbs': round(carbs),
            'fat': round(fat)
        }
    }
    
    return jsonify(response)

@app.route('/generate_meal_plan', methods=['POST'])
def generate_meal_plan():
    data = request.json
    target_calories = data.get('target_calories', 2000)
    diet_preference = data.get('diet_preference', 'non-vegetarian')
    
    # Sample meal plans based on diet preference
    meal_plans = {
        'vegetarian': {
            'breakfast': [
                'Oatmeal with berries and nuts',
                'Greek yogurt with granola and honey',
                'Avocado toast with eggs'
            ],
            'lunch': [
                'Quinoa salad with mixed vegetables',
                'Vegetable stir-fry with tofu',
                'Lentil soup with whole grain bread'
            ],
            'dinner': [
                'Grilled vegetable pasta',
                'Chickpea curry with brown rice',
                'Stuffed bell peppers with quinoa'
            ],
            'snacks': [
                'Mixed nuts and dried fruits',
                'Hummus with vegetable sticks',
                'Fruit smoothie with protein powder'
            ]
        },
        'non-vegetarian': {
            'breakfast': [
                'Scrambled eggs with whole grain toast',
                'Chicken and vegetable omelette',
                'Protein smoothie with banana and peanut butter'
            ],
            'lunch': [
                'Grilled chicken salad',
                'Salmon with quinoa and vegetables',
                'Turkey wrap with whole grain tortilla'
            ],
            'dinner': [
                'Grilled fish with sweet potato and greens',
                'Lean beef stir-fry with brown rice',
                'Baked chicken with roasted vegetables'
            ],
            'snacks': [
                'Greek yogurt with berries',
                'Hard-boiled eggs',
                'Protein bar'
            ]
        },
        'vegan': {
            'breakfast': [
                'Smoothie bowl with plant-based protein',
                'Tofu scramble with vegetables',
                'Chia pudding with almond milk'
            ],
            'lunch': [
                'Vegan Buddha bowl',
                'Lentil and vegetable curry',
                'Vegan wrap with hummus'
            ],
            'dinner': [
                'Vegan chili with brown rice',
                'Stuffed portobello mushrooms',
                'Vegan stir-fry with tofu'
            ],
            'snacks': [
                'Roasted chickpeas',
                'Vegan protein shake',
                'Fruit and nut mix'
            ]
        }
    }
    
    # Select random meals for each category
    import random
    selected_plan = meal_plans.get(diet_preference.lower(), meal_plans['non-vegetarian'])
    daily_plan = {
        'breakfast': random.choice(selected_plan['breakfast']),
        'lunch': random.choice(selected_plan['lunch']),
        'dinner': random.choice(selected_plan['dinner']),
        'snacks': random.choice(selected_plan['snacks'])
    }
    
    return jsonify({
        'status': 'success',
        'daily_plan': daily_plan,
        'calories': target_calories,
        'diet_preference': diet_preference
    })

@app.route('/generate_workout_plan', methods=['POST'])
def generate_workout_plan():
    data = request.json
    activity_level = data.get('activity_level', 'moderate')
    goal = data.get('goal', 'maintain')
    
    # Sample workout plans based on activity level and goal
    workout_plans = {
        'sedentary': {
            'monday': '30-minute brisk walk + 10-minute stretching',
            'tuesday': 'Rest day',
            'wednesday': '30-minute yoga session',
            'thursday': 'Rest day',
            'friday': '30-minute light cardio',
            'saturday': 'Rest day',
            'sunday': '30-minute stretching and mobility exercises'
        },
        'moderate': {
            'monday': '45-minute strength training (upper body)',
            'tuesday': '30-minute cardio (running/cycling)',
            'wednesday': '45-minute strength training (lower body)',
            'thursday': '30-minute HIIT workout',
            'friday': '45-minute strength training (full body)',
            'saturday': 'Rest day',
            'sunday': '45-minute yoga or stretching'
        },
        'active': {
            'monday': '60-minute strength training (push day)',
            'tuesday': '45-minute cardio + core workout',
            'wednesday': '60-minute strength training (pull day)',
            'thursday': '45-minute HIIT + plyometrics',
            'friday': '60-minute strength training (legs)',
            'saturday': '45-minute cardio + core workout',
            'sunday': '60-minute active recovery (yoga/stretching)'
        }
    }
    
    # Adjust workout plan based on goal
    base_plan = workout_plans.get(activity_level.lower(), workout_plans['moderate'])
    if goal.lower() == 'lose weight':
        # Add more cardio
        base_plan['tuesday'] = '45-minute cardio (running/cycling) + 15-minute HIIT'
        base_plan['thursday'] = '45-minute HIIT workout + 15-minute cardio'
    elif goal.lower() == 'gain muscle':
        # Add more strength training
        base_plan['monday'] = '60-minute strength training (upper body) + 15-minute core'
        base_plan['wednesday'] = '60-minute strength training (lower body) + 15-minute core'
        base_plan['friday'] = '60-minute strength training (full body)'
    
    return jsonify({
        'status': 'success',
        'weekly_plan': base_plan,
        'activity_level': activity_level,
        'goal': goal
    })

@app.route('/text_to_speech', methods=['POST'])
def text_to_speech():
    text = request.json.get('text')
    if not text:
        return jsonify({'error': 'No text provided'}), 400
    
    tts = gTTS(text=text, lang='en')
    filename = f"speech_{datetime.now().strftime('%Y%m%d_%H%M%S')}.mp3"
    tts.save(filename)
    
    return send_file(filename, as_attachment=True)

@app.route('/chat', methods=['POST'])
def chat():
    try:
        data = request.json
        user_message = data.get('message', '')
        user_context = data.get('context', {})
        
        # If OpenAI client is not available, use a simple rule-based response
        if not client:
            return jsonify({
                'status': 'success',
                'response': get_fallback_response(user_message, user_context)
            })
        
        # Create a context-aware prompt
        system_prompt = f"""You are an AI Diet and Fitness Coach assistant. The user has the following context:
        - Diet Preference: {user_context.get('diet_preference', 'Not specified')}
        - Activity Level: {user_context.get('activity_level', 'Not specified')}
        - Fitness Goal: {user_context.get('goal', 'Not specified')}
        - Daily Calorie Target: {user_context.get('target_calories', 'Not specified')}
        
        Provide helpful, accurate, and personalized advice about diet and fitness based on this context.
        If the user asks about specific exercises or meals, make sure your suggestions align with their preferences and goals.
        Always maintain a professional and encouraging tone."""
        
        # Get response from OpenAI
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_message}
            ],
            temperature=0.7,
            max_tokens=500
        )
        
        return jsonify({
            'status': 'success',
            'response': response.choices[0].message.content
        })
        
    except Exception as e:
        return jsonify({
            'status': 'success',  # Still return success to keep the chat working
            'response': get_fallback_response(user_message, user_context)
        })

def get_fallback_response(user_message, user_context):
    """Provide simple rule-based responses when OpenAI is not available"""
    message = user_message.lower()
    diet_pref = user_context.get('diet_preference', '').lower()
    activity = user_context.get('activity_level', '').lower()
    goal = user_context.get('goal', '').lower()
    target_calories = user_context.get('target_calories', 0)
    
    # Duration/timeline related questions
    if any(phrase in message for phrase in ['how many days', 'how long', 'duration', 'timeline']):
        if goal == 'lose weight':
            return "For weight loss, you should follow this plan for at least 8-12 weeks to see significant results. Aim to lose 1-2 pounds per week for sustainable weight loss. Remember to track your progress and adjust the plan as needed."
        elif goal == 'gain muscle':
            return "For muscle gain, commit to this plan for at least 12-16 weeks. Muscle building takes time, and you should expect to gain about 0.5-1 pound of lean muscle per week when following the nutrition and workout plans consistently."
        else:
            return "For maintaining your fitness level and weight, this is meant to be a sustainable lifestyle plan. Start with a 12-week commitment, then adjust based on your progress and goals. Regular check-ins every 4 weeks will help ensure you're staying on track."

    # Meal frequency questions
    elif any(phrase in message for phrase in ['how many meals', 'meal frequency', 'when to eat']):
        if target_calories > 2000:
            return f"With your target of {target_calories} calories, aim for 5-6 smaller meals throughout the day. This helps maintain steady energy levels and makes it easier to meet your caloric needs."
        else:
            return f"With your target of {target_calories} calories, aim for 3 main meals and 1-2 snacks per day. Space your meals every 3-4 hours to maintain stable blood sugar levels."

    # Exercise frequency questions
    elif any(phrase in message for phrase in ['how often', 'exercise frequency', 'workout frequency']):
        if activity == 'sedentary':
            return "Start with 3 days per week of light exercise, focusing on building consistency. Include rest days between workouts to allow your body to adjust to the new routine."
        elif activity == 'moderate':
            return "Aim for 4-5 workout days per week, alternating between strength training and cardio. This gives you enough stimulus for progress while allowing adequate recovery."
        else:
            return "With your active lifestyle, you can train 5-6 days per week. Just ensure you're taking at least one full rest day and listening to your body's recovery needs."

    # Rest and recovery questions
    elif any(word in message for word in ['rest', 'recovery', 'break', 'rest day']):
        if activity == 'active':
            return "Take at least one full rest day per week. Active recovery like light walking or yoga can be done on other days when you feel you need extra recovery."
        else:
            return "Include 2-3 rest days per week, spacing them between workout days. This helps prevent burnout and allows proper recovery, especially when you're starting out."

    # Progress tracking questions
    elif any(phrase in message for phrase in ['track progress', 'measure results', 'check progress']):
        if goal == 'lose weight':
            return "Track your progress weekly by: 1) Weighing yourself first thing in the morning, 2) Taking body measurements, 3) Tracking your energy levels and workout performance, 4) Taking progress photos monthly."
        elif goal == 'gain muscle':
            return "Monitor your progress by: 1) Tracking your strength gains in workouts, 2) Taking monthly body measurements, 3) Weighing yourself weekly, 4) Taking progress photos every 4 weeks."
        else:
            return "Keep track of your maintenance by: 1) Monthly body measurements, 2) Weekly weigh-ins, 3) Tracking your energy levels and workout performance, 4) Regular progress photos if desired."

    # Default responses based on context
    elif 'meal' in message or 'food' in message or 'eat' in message:
        if diet_pref == 'vegetarian':
            return "For your vegetarian diet, I recommend focusing on plant-based proteins like beans, lentils, and tofu. Include plenty of vegetables and whole grains for balanced nutrition. Aim to eat every 3-4 hours to maintain energy levels."
        elif diet_pref == 'vegan':
            return "As a vegan, make sure to get enough protein from sources like tempeh, seitan, and legumes. Include a variety of fruits, vegetables, and whole grains in your meals. Consider B12 supplementation and eat regularly throughout the day."
        else:
            return "For a balanced diet, include lean proteins, whole grains, and plenty of vegetables. Try to have regular meals and healthy snacks throughout the day. Timing your meals every 3-4 hours helps maintain stable energy levels."
    
    elif 'exercise' in message or 'workout' in message:
        if activity == 'sedentary':
            return "Start with light activities like walking, stretching, or yoga. Aim for 30 minutes of activity most days of the week, with plenty of rest between sessions as you build up your fitness level."
        elif activity == 'moderate':
            return "Include a mix of cardio and strength training. Try to exercise 3-5 times per week for 30-45 minutes, allowing for rest days between strength training sessions."
        else:
            return "For your active lifestyle, focus on a combination of strength training, cardio, and flexibility exercises. Make sure to include rest days for recovery, and vary your workout intensity throughout the week."

    # Greeting or unknown query
    else:
        return "I can help you with specific questions about your meal plan, workout routine, exercise frequency, rest days, and progress tracking. What would you like to know more about?"

if __name__ == '__main__':
    app.run(debug=True) 