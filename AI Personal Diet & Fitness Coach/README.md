# AI Personal Diet & Fitness Coach

A web-based application that provides personalized diet and fitness plans based on user input and AI-powered recommendations.

## Features

- Personalized calorie and macronutrient calculations
- Customized meal plans based on dietary preferences
- Tailored workout recommendations
- Text-to-speech functionality for plan reading
- Downloadable plans in text format

## Prerequisites

- Python 3.8 or higher
- pip (Python package manager)

## Setup Instructions

1. Clone the repository:
```bash
git clone <repository-url>
cd ai-personal-diet-fitness-coach
```

2. Create a virtual environment (recommended):
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install required packages:
```bash
pip install -r requirements.txt
```

4. Create a `.env` file in the project root and add your API keys:
```
NUTRITIONIX_APP_ID=your_app_id
NUTRITIONIX_APP_KEY=your_app_key
```

5. Run the application:
```bash
python app.py
```

6. Open your web browser and navigate to:
```
http://localhost:5000
```

## API Integration

This application uses the following APIs:

- Nutritionix API for meal planning and nutrition data
- (Additional APIs to be implemented)

## Project Structure

```
ai-personal-diet-fitness-coach/
├── app.py                 # Main Flask application
├── requirements.txt       # Python dependencies
├── .env                  # Environment variables
├── static/
│   ├── style.css         # CSS styles
│   └── script.js         # Frontend JavaScript
└── templates/
    └── index.html        # Main HTML template
```

## Contributing

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgments

- Flask web framework
- Nutritionix API
- gTTS for text-to-speech functionality 