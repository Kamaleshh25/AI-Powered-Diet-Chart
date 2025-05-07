document.addEventListener('DOMContentLoaded', () => {
    const form = document.getElementById('health-form');
    const resultsSection = document.getElementById('results');
    const chatSection = document.getElementById('chat-section');
    const speakButton = document.getElementById('speak-plan');
    const downloadButton = document.getElementById('download-plan');
    const chatInput = document.getElementById('chat-input');
    const sendButton = document.getElementById('send-message');
    const chatMessages = document.getElementById('chat-messages');
    
    let userContext = {}; // Store user context globally

    // Initialize chat functionality
    function initializeChat() {
        // Clear any existing messages
        chatMessages.innerHTML = '';
        
        // Add welcome message
        addMessageToChat('assistant', 'Hello! I\'m your AI Diet and Fitness Coach. How can I help you with your personalized plan?');
        
        // Set up event listeners for chat
        sendButton.addEventListener('click', sendMessage);
        chatInput.addEventListener('keypress', (e) => {
            if (e.key === 'Enter') {
                sendMessage();
            }
        });
    }

    function addMessageToChat(role, content) {
        const messageDiv = document.createElement('div');
        messageDiv.classList.add('chat-message');
        messageDiv.classList.add(role + '-message');
        messageDiv.textContent = content;
        chatMessages.appendChild(messageDiv);
        chatMessages.scrollTop = chatMessages.scrollHeight;
    }

    async function sendMessage() {
        const message = chatInput.value.trim();
        if (!message) return;

        // Add user message to chat
        addMessageToChat('user', message);
        chatInput.value = '';

        try {
            console.log('Sending message:', message);
            console.log('User context:', userContext);
            
            const response = await fetch('/chat', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    message: message,
                    context: userContext
                })
            });

            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }

            const data = await response.json();
            console.log('Received response:', data);
            
            if (data.status === 'success') {
                addMessageToChat('assistant', data.response);
            } else {
                throw new Error(data.message || 'Unknown error occurred');
            }
        } catch (error) {
            console.error('Error in sendMessage:', error);
            addMessageToChat('assistant', 'I apologize, but I encountered an error. Could you please try rephrasing your question?');
        }
    }

    form.addEventListener('submit', async (e) => {
        e.preventDefault();
        
        const formData = {
            name: document.getElementById('name').value,
            age: document.getElementById('age').value,
            gender: document.getElementById('gender').value,
            weight: document.getElementById('weight').value,
            height: document.getElementById('height').value,
            activity_level: document.getElementById('activity-level').value,
            goal: document.getElementById('goal').value,
            diet_preference: document.getElementById('diet-preference').value
        };

        try {
            // Calculate nutritional needs
            const response = await fetch('/calculate', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify(formData)
            });

            if (!response.ok) {
                throw new Error('Network response was not ok');
            }

            const data = await response.json();
            
            // Update the results section
            document.getElementById('bmr').textContent = data.bmr;
            document.getElementById('tdee').textContent = data.tdee;
            document.getElementById('target-calories').textContent = data.target_calories;
            document.getElementById('protein').textContent = data.macros.protein;
            document.getElementById('carbs').textContent = data.macros.carbs;
            document.getElementById('fats').textContent = data.macros.fat;

            // Store user context for chat
            userContext = {
                diet_preference: formData.diet_preference,
                activity_level: formData.activity_level,
                goal: formData.goal,
                target_calories: data.target_calories,
                bmr: data.bmr,
                tdee: data.tdee,
                macros: data.macros
            };

            // Generate meal plan
            const mealPlanResponse = await fetch('/generate_meal_plan', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify(formData)
            });

            if (!mealPlanResponse.ok) {
                throw new Error('Meal plan generation failed');
            }

            const mealPlanData = await mealPlanResponse.json();
            document.getElementById('meal-plan').innerHTML = formatMealPlan(mealPlanData);

            // Generate workout plan
            const workoutPlanResponse = await fetch('/generate_workout_plan', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify(formData)
            });

            if (!workoutPlanResponse.ok) {
                throw new Error('Workout plan generation failed');
            }

            const workoutPlanData = await workoutPlanResponse.json();
            document.getElementById('workout-plan').innerHTML = formatWorkoutPlan(workoutPlanData);

            // Show results and chat sections
            resultsSection.classList.remove('hidden');
            chatSection.classList.remove('hidden');
            
            // Initialize chat
            initializeChat();
            
        } catch (error) {
            console.error('Error:', error);
            alert('An error occurred while processing your request. Please try again.');
        }
    });

    speakButton.addEventListener('click', async () => {
        const planText = generatePlanText();
        try {
            const response = await fetch('/text_to_speech', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ text: planText })
            });

            if (response.ok) {
                const blob = await response.blob();
                const audio = new Audio(URL.createObjectURL(blob));
                audio.play();
            }
        } catch (error) {
            console.error('Error:', error);
            alert('An error occurred while generating speech. Please try again.');
        }
    });

    downloadButton.addEventListener('click', () => {
        const planText = generatePlanText();
        const blob = new Blob([planText], { type: 'text/plain' });
        const url = URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = 'personalized_plan.txt';
        document.body.appendChild(a);
        a.click();
        document.body.removeChild(a);
        URL.revokeObjectURL(url);
    });

    function formatMealPlan(data) {
        if (!data.daily_plan) return '<p>No meal plan available</p>';
        
        const plan = data.daily_plan;
        return `
            <div class="meal-plan-details">
                <h4>Daily Meal Plan (${data.calories} calories)</h4>
                <ul>
                    <li><strong>Breakfast:</strong> ${plan.breakfast}</li>
                    <li><strong>Lunch:</strong> ${plan.lunch}</li>
                    <li><strong>Dinner:</strong> ${plan.dinner}</li>
                    <li><strong>Snack:</strong> ${plan.snacks}</li>
                </ul>
                <p class="diet-preference">Diet Preference: ${data.diet_preference}</p>
            </div>
        `;
    }

    function formatWorkoutPlan(data) {
        if (!data.weekly_plan) return '<p>No workout plan available</p>';
        
        const plan = data.weekly_plan;
        return `
            <div class="workout-plan-details">
                <h4>Weekly Workout Plan (${data.activity_level} activity level)</h4>
                <ul>
                    <li><strong>Monday:</strong> ${plan.monday}</li>
                    <li><strong>Tuesday:</strong> ${plan.tuesday}</li>
                    <li><strong>Wednesday:</strong> ${plan.wednesday}</li>
                    <li><strong>Thursday:</strong> ${plan.thursday}</li>
                    <li><strong>Friday:</strong> ${plan.friday}</li>
                    <li><strong>Saturday:</strong> ${plan.saturday}</li>
                    <li><strong>Sunday:</strong> ${plan.sunday}</li>
                </ul>
                <p class="fitness-goal">Fitness Goal: ${data.goal}</p>
            </div>
        `;
    }

    function generatePlanText() {
        const bmr = document.getElementById('bmr').textContent;
        const tdee = document.getElementById('tdee').textContent;
        const targetCalories = document.getElementById('target-calories').textContent;
        const protein = document.getElementById('protein').textContent;
        const carbs = document.getElementById('carbs').textContent;
        const fats = document.getElementById('fats').textContent;

        return `Your Personalized Diet & Fitness Plan

Daily Caloric Needs:
- BMR: ${bmr} calories
- TDEE: ${tdee} calories
- Target Calories: ${targetCalories} calories

Macronutrient Breakdown:
- Protein: ${protein}g
- Carbohydrates: ${carbs}g
- Fats: ${fats}g

Meal Plan:
${document.getElementById('meal-plan').textContent}

Workout Plan:
${document.getElementById('workout-plan').textContent}`;
    }
}); 