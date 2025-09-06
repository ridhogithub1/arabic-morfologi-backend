from flask import Flask, request, jsonify
from flask_cors import CORS
import requests
import json
import random
import os

app = Flask(__name__)
CORS(app)

# Gemini API configuration
GEMINI_API_KEYS = [
    "AIzaSyAPFGdmEGAolRlOLG53k8VVE3IdpuywfSs",
    "AIzaSyABMns2VWw5IuV6PYJhG1TJbIHl6-iJGGk",
]
GEMINI_TEXT_URL = "https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent"

def get_random_api_key():
    """Get a random API key from the list"""
    return random.choice(GEMINI_API_KEYS)

def analyze_arabic_morphology(text):
    """Analyze Arabic text morphology using Gemini API"""
    api_key = get_random_api_key()
    url = f"{GEMINI_TEXT_URL}?key={api_key}"
    
    prompt = f"""
    Please analyze the Arabic morphology of the following text: "{text}"

    For each word in the text, provide:
    1. الكلمة الأصلية (Original word)
    2. الجذر (Root letters - usually 3 letters)
    3. حرف الزيادة (Extra letters such as ا، و، ي، ه، ن، ء if present)
    4. الوزن (Pattern/Weight - like فعل، فاعل، مفعول، etc.)
    5. نوع الكلمة (Word type: اسم/فعل/حرف)
    6. الزمن (For verbs: ماضي/مضارع/أمر)
    7. كلمات مشتقة (Related/derived words from the same root)
    8. المعنى (Meaning in Arabic and English)

    Please format your response as a JSON object with the following structure:
    {{
        "analysis": [
            {{
                "word": "الكلمة",
                "root": "ج ذ ر",
                "extra_letters": ["ا"], 
                "pattern": "الوزن",
                "type": "نوع الكلمة",
                "tense": "الزمن (if applicable)",
                "related_words": ["كلمة1", "كلمة2", "كلمة3"],
                "meaning_arabic": "المعنى بالعربية",
                "meaning_english": "English meaning"
            }}
        ],
        "summary": "ملخص عام عن النص المُحلل"
    }}

    Respond only with the JSON object, no additional text.
    """

    payload = {
        "contents": [
            {
                "parts": [
                    {
                        "text": prompt
                    }
                ]
            }
        ],
        "generationConfig": {
            "temperature": 0.1,
            "topK": 40,
            "topP": 0.95,
            "maxOutputTokens": 2048,
        }
    }
    
    headers = {
        "Content-Type": "application/json"
    }
    
    try:
        response = requests.post(url, headers=headers, json=payload, timeout=30)
        response.raise_for_status()
        
        result = response.json()
        
        if 'candidates' in result and len(result['candidates']) > 0:
            content = result['candidates'][0]['content']['parts'][0]['text']
            
            try:
                if content.startswith('```json'):
                    content = content.replace('```json', '').replace('```', '').strip()
                elif content.startswith('```'):
                    content = content.replace('```', '').strip()
                
                morphology_data = json.loads(content)
                return morphology_data
            except json.JSONDecodeError:
                return {
                    "error": "Could not parse JSON response",
                    "raw_response": content,
                    "analysis": [],
                    "summary": "تعذر تحليل النص بشكل صحيح"
                }
        else:
            return {
                "error": "No response from Gemini API",
                "analysis": [],
                "summary": "لم يتم الحصول على رد من الخدمة"
            }
            
    except requests.exceptions.Timeout:
        return {
            "error": "Request timeout",
            "analysis": [],
            "summary": "انتهت مهلة الطلب"
        }
    except requests.exceptions.RequestException as e:
        return {
            "error": f"API request failed: {str(e)}",
            "analysis": [],
            "summary": "حدث خطأ في الاتصال بالخدمة"
        }

@app.route('/')
def home():
    return jsonify({
        "message": "Arabic Morphology API is running!",
        "status": "healthy",
        "endpoints": ["/", "/analyze", "/tasrif", "/health"]
    })

@app.route('/analyze', methods=['POST', 'OPTIONS'])
def analyze_text():
    if request.method == 'OPTIONS':
        response = jsonify({'status': 'ok'})
        response.headers.add('Access-Control-Allow-Origin', '*')
        response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization')
        response.headers.add('Access-Control-Allow-Methods', 'GET,PUT,POST,DELETE,OPTIONS')
        return response
        
    try:
        data = request.get_json()
        
        if not data or 'text' not in data:
            return jsonify({
                "error": "No text provided",
                "message": "يرجى إدخال نص للتحليل"
            }), 400
        
        arabic_text = data['text'].strip()
        
        if not arabic_text:
            return jsonify({
                "error": "Empty text",
                "message": "النص فارغ"
            }), 400
        
        result = analyze_arabic_morphology(arabic_text)
        
        return jsonify({
            "success": True,
            "input_text": arabic_text,
            "result": result
        })
        
    except Exception as e:
        return jsonify({
            "error": f"Server error: {str(e)}",
            "message": "حدث خطأ في الخادم"
        }), 500

def get_rule_by_root(root):
    """Determines the Tasrif Istilahi rule for a given root."""
    rule_map = {
        'نصر': 1, 'كتب': 1,
        'ضرب': 2, 'جلس': 2,
        'فتح': 3, 'ذهب': 3,
        'علم': 4, 'شرب': 4,
        'كرم': 5, 'حسن': 5,
        'حسب': 6, 'ورث': 6,
    }
    return rule_map.get(root, 1)

def generate_tasrif_isim(root):
    """Generate different forms of Arabic nouns based on the root letters."""
    if len(root) < 3:
        return []
    
    r1, r2, r3 = root[0], root[1], root[2]
    
    noun_patterns = [
        {
            "pattern_name": "فَاعِل",
            "singular": f"{r1}َا{r2}ِ{r3}ٌ",
            "dual_masculine": f"{r1}َا{r2}ِ{r3}َانِ",
            "dual_feminine": f"{r1}َا{r2}ِ{r3}َتَانِ",
            "plural_masculine": f"{r1}َا{r2}ِ{r3}ُونَ",
            "plural_feminine": f"{r1}َا{r2}ِ{r3}َاتٌ",
            "broken_plural": f"{r1}ُ{r2}َّا{r3}ٌ"
        }
    ]
    
    selected_pattern = noun_patterns[0]
    
    tasrif_data = [
        ("المفرد (Singular)", selected_pattern["singular"]),
        ("المثنى المذكر (Dual Masculine)", selected_pattern["dual_masculine"]),
        ("المثنى المؤنث (Dual Feminine)", selected_pattern["dual_feminine"]),
        ("الجمع المذكر السالم (Sound Masculine Plural)", selected_pattern["plural_masculine"]),
        ("الجمع المؤنث السالم (Sound Feminine Plural)", selected_pattern["plural_feminine"]),
        ("جمع التكسير (Broken Plural)", selected_pattern["broken_plural"]),
    ]
    
    return tasrif_data

@app.route('/tasrif', methods=['POST', 'OPTIONS'])
def generate_tasrif():
    if request.method == 'OPTIONS':
        response = jsonify({'status': 'ok'})
        response.headers.add('Access-Control-Allow-Origin', '*')
        response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization')
        response.headers.add('Access-Control-Allow-Methods', 'GET,PUT,POST,DELETE,OPTIONS')
        return response
        
    try:
        data = request.get_json()
        if not data or 'root' not in data or 'mode' not in data:
            return jsonify({"error": "Need root and mode"}), 400

        root = data['root'].strip().replace(' ', '')
        mode = data['mode']

        if len(root) < 3:
            return jsonify({"error": "Invalid root"}), 400

        r1, r2, r3 = root[0], root[1], root[2]

        if mode == "istilahi":
            rule_number = get_rule_by_root(root)
            
            past, mudari, masdar, masdar_mimi, ism_fael, ism_mafool, amr, nahi, zaman, makan, alat = "", "", "", "", "", "", "", "", "", "", ""
            
            if rule_number == 1:
                past = f"{r1}َ{r2}َ{r3}َ"
                mudari = f"يَ{r1}ْ{r2}ُ{r3}ُ"
                masdar = f"{r1}َ{r2}ْ{r3}ًا"
                masdar_mimi = f"مَ{r1}ْ{r2}َ{r3}ًا"
                ism_fael = f"{r1}َا{r2}ِ{r3}ٌ"
                ism_mafool = f"مَ{r1}ْ{r2}ُو{r3}ٌ"
                amr = f"اُ{r1}ْ{r2}ُ{r3}ْ"
                nahi = f"لَا تَ{r1}ْ{r2}ُ{r3}ْ"
                zaman = f"مَ{r1}ْ{r2}َ{r3}ٌ"
                makan = f"مَ{r1}ْ{r2}َ{r3}ٌ"
                alat = f"مِ{r1}ْ{r2}َ{r3}ٌ"
            elif rule_number == 2:
                past = f"{r1}َ{r2}َ{r3}َ"
                mudari = f"يَ{r1}ْ{r2}ِ{r3}ُ"
                masdar = f"{r1}َ{r2}ْ{r3}ًا"
                masdar_mimi = f"مَ{r1}ْ{r2}َ{r3}ًا"
                ism_fael = f"{r1}َا{r2}ِ{r3}ٌ"
                ism_mafool = f"مَ{r1}ْ{r2}ُو{r3}ٌ"
                amr = f"اِ{r1}ْ{r2}ِ{r3}ْ"
                nahi = f"لَا تَ{r1}ْ{r2}ِ{r3}ْ"
                zaman = f"مَ{r1}ْ{r2}ِ{r3}ٌ"
                makan = f"مَ{r1}ْ{r2}ِ{r3}ٌ"
                alat = f"مِ{r1}ْ{r2}َ{r3}ٌ"
            # Add other rules as needed...
            else:
                # Default rule 1 pattern
                past = f"{r1}َ{r2}َ{r3}َ"
                mudari = f"يَ{r1}ْ{r2}ُ{r3}ُ"
                masdar = f"{r1}َ{r2}ْ{r3}ًا"
                masdar_mimi = f"مَ{r1}ْ{r2}َ{r3}ًا"
                ism_fael = f"{r1}َا{r2}ِ{r3}ٌ"
                ism_mafool = f"مَ{r1}ْ{r2}ُو{r3}ٌ"
                amr = f"اُ{r1}ْ{r2}ُ{r3}ْ"
                nahi = f"لَا تَ{r1}ْ{r2}ُ{r3}ْ"
                zaman = f"مَ{r1}ْ{r2}َ{r3}ٌ"
                makan = f"مَ{r1}ْ{r2}َ{r3}ٌ"
                alat = f"مِ{r1}ْ{r2}َ{r3}ٌ"

            tasrif_data = [
                ("1. الفعل الماضي", past),
                ("2. الفعل المضارع", mudari),
                ("3. المصدر", masdar),
                ("4. المصدر الميمي", masdar_mimi),
                ("5. اسم الفاعل", ism_fael),
                ("6. اسم المفعول", ism_mafool),
                ("7. فعل الأمر", amr),
                ("8. فعل النهي", nahi),
                ("9. اسم الزمان", zaman),
                ("10. اسم المكان", makan),
                ("11. اسم الآلة", alat),
            ]
        
        elif mode == "lughowiy":
            tasrif_data = [
                ("هُوَ", f"{r1}َ{r2}َ{r3}َ"),
                ("هما (م)", f"{r1}َ{r2}َ{r3}َا"),
                ("هم", f"{r1}َ{r2}َ{r3}ُوا"),
                ("هي", f"{r1}َ{r2}َ{r3}َتْ"),
                ("هما (ف)", f"{r1}َ{r2}َ{r3}َتَا"),
                ("هنّ", f"{r1}َ{r2}َ{r3}ْنَ"),
                ("أنتَ", f"{r1}َ{r2}َ{r3}ْتَ"),
                ("أنتما (م)", f"{r1}َ{r2}َ{r3}ْتُمَا"),
                ("أنتم", f"{r1}َ{r2}َ{r3}ْتُمْ"),
                ("أنتِ", f"{r1}َ{r2}َ{r3}ْتِ"),
                ("أنتما (ف)", f"{r1}َ{r2}َ{r3}ْتُمَا"),
                ("أنتنّ", f"{r1}َ{r2}َ{r3}ْتُنَّ"),
                ("أنا", f"{r1}َ{r2}َ{r3}ْتُ"),
                ("نحن", f"{r1}َ{r2}َ{r3}ْنَا"),
            ]
        
        elif mode == "isim":
            tasrif_data = generate_tasrif_isim(root)
        
        else:
            return jsonify({"error": "Invalid mode"}), 400

        return jsonify({"success": True, "tasrif": tasrif_data, "root": root})

    except Exception as e:
        return jsonify({"error": f"Server error: {str(e)}"}), 500

@app.route('/health', methods=['GET'])
def health_check():
    return jsonify({"status": "healthy", "message": "Server is running"})

# This is important for Vercel
if __name__ == '__main__':
    app.run(debug=False)
else:
    # This is what Vercel will use
    application = app
