# from flask import Flask, request, jsonify
# from flask_cors import CORS
# import requests
# import json
# import random
# from collections import OrderedDict

# app = Flask(__name__)
# CORS(app)  # Enable CORS for all routes

# # Gemini API configuration
# GEMINI_API_KEYS = [
#     "AIzaSyABMns2VWw5IuV6PYJhG1TJbIHl6-iJGGk",
#     "AIzaSyAPFGdmEGAolRlOLG53k8VVE3IdpuywfSs"
# ]
# GEMINI_TEXT_URL = "https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent"

# def get_random_api_key():
#     """Get a random API key from the list"""
#     return random.choice(GEMINI_API_KEYS)

# def analyze_arabic_morphology(text):
#     """Analyze Arabic text morphology using Gemini API"""
#     api_key = get_random_api_key()
#     url = f"{GEMINI_TEXT_URL}?key={api_key}"
    
#     prompt = f"""
#     Please analyze the Arabic morphology of the following text: "{text}"

#     For each word in the text, provide:
#     1. الكلمة الأصلية (Original word)
#     2. الجذر (Root letters - usually 3 letters)
#     3. حرف الزيادة (Extra letters such as ا، و، ي، ه، ن، ء if present)
#     4. الوزن (Pattern/Weight - like فعل، فاعل، مفعول، etc.)
#     5. نوع الكلمة (Word type: اسم/فعل/حرف)
#     6. الزمن (For verbs: ماضي/مضارع/أمر)
#     7. كلمات مشتقة (Related/derived words from the same root)
#     8. المعنى (Meaning in Arabic and English)

#     Please format your response as a JSON object with the following structure:
#     {{
#         "analysis": [
#             {{
#                 "word": "الكلمة",
#                 "root": "ج ذ ر",
#                 "extra_letters": ["ا"], 
#                 "pattern": "الوزن",
#                 "type": "نوع الكلمة",
#                 "tense": "الزمن (if applicable)",
#                 "related_words": ["كلمة1", "كلمة2", "كلمة3"],
#                 "meaning_arabic": "المعنى بالعربية",
#                 "meaning_english": "English meaning"
#             }}
#         ],
#         "summary": "ملخص عام عن النص المُحلل"
#     }}

#     Respond only with the JSON object, no additional text.
#     """

    
#     payload = {
#         "contents": [
#             {
#                 "parts": [
#                     {
#                         "text": prompt
#                     }
#                 ]
#             }
#         ],
#         "generationConfig": {
#             "temperature": 0.1,
#             "topK": 40,
#             "topP": 0.95,
#             "maxOutputTokens": 2048,
#         }
#     }
    
#     headers = {
#         "Content-Type": "application/json"
#     }
    
#     try:
#         response = requests.post(url, headers=headers, json=payload)
#         response.raise_for_status()
        
#         result = response.json()
        
#         if 'candidates' in result and len(result['candidates']) > 0:
#             content = result['candidates'][0]['content']['parts'][0]['text']
            
#             # Try to parse the JSON response
#             try:
#                 # Clean the response if it contains markdown code blocks
#                 if content.startswith('```json'):
#                     content = content.replace('```json', '').replace('```', '').strip()
#                 elif content.startswith('```'):
#                     content = content.replace('```', '').strip()
                
#                 morphology_data = json.loads(content)
#                 return morphology_data
#             except json.JSONDecodeError:
#                 # If JSON parsing fails, return the raw content
#                 return {
#                     "error": "Could not parse JSON response",
#                     "raw_response": content,
#                     "analysis": [],
#                     "summary": "تعذر تحليل النص بشكل صحيح"
#                 }
#         else:
#             return {
#                 "error": "No response from Gemini API",
#                 "analysis": [],
#                 "summary": "لم يتم الحصول على رد من الخدمة"
#             }
            
#     except requests.exceptions.RequestException as e:
#         return {
#             "error": f"API request failed: {str(e)}",
#             "analysis": [],
#             "summary": "حدث خطأ في الاتصال بالخدمة"
#         }

# @app.route('/')
# def home():
#     return jsonify({"message": "Arabic Morphology API is running!"})

# @app.route('/analyze', methods=['POST'])
# def analyze_text():
#     try:
#         data = request.get_json()
        
#         if not data or 'text' not in data:
#             return jsonify({
#                 "error": "No text provided",
#                 "message": "يرجى إدخال نص للتحليل"
#             }), 400
        
#         arabic_text = data['text'].strip()
        
#         if not arabic_text:
#             return jsonify({
#                 "error": "Empty text",
#                 "message": "النص فارغ"
#             }), 400
        
#         # Analyze the text
#         result = analyze_arabic_morphology(arabic_text)
        
#         return jsonify({
#             "success": True,
#             "input_text": arabic_text,
#             "result": result
#         })
        
#     except Exception as e:
#         return jsonify({
#             "error": f"Server error: {str(e)}",
#             "message": "حدث خطأ في الخادم"
#         }), 500

# def get_rule_by_root(root):
#     """
#     Determines the Tasrif Istilahi rule (Hukum) for a given root.
#     This is a simplified approach for demonstration purposes, mapping
#     common roots to their respective rule numbers.
#     """
#     # Map roots to their rule number based on the provided patterns
#     rule_map = {
#         'نصر': 1, 'كتب': 1, # Rule 1: فَعَلَ - يَفْعُلُ
#         'ضرب': 2, 'جلس': 2, # Rule 2: فَعَلَ - يَفْعِلُ
#         'فتح': 3, 'ذهب': 3, # Rule 3: فَعَلَ - يَفْعَلُ
#         'علم': 4, 'شرب': 4, # Rule 4: فَعِلَ - يَفْعَلُ
#         'كرم': 5, 'حسن': 5, # Rule 5: فَعُلَ - يَفْعُلُ
#         'حسب': 6, 'ورث': 6, # Rule 6: فَعِلَ - يَفْعِلُ
#     }
#     return rule_map.get(root, 1) # Default to rule 1 if root is not found

# @app.route('/tasrif', methods=['POST'])
# def generate_tasrif():
#     try:
#         data = request.get_json()
#         if not data or 'root' not in data or 'mode' not in data:
#             return jsonify({"error": "Need root and mode"}), 400

#         # Clean the root input
#         root = data['root'].strip().replace(' ', '')
#         mode = data['mode']

#         if len(root) < 3:
#             return jsonify({"error": "Invalid root"}), 400

#         r1, r2, r3 = root[0], root[1], root[2]

#         if mode == "istilahi":
#             # Get the correct rule number for the given root
#             rule_number = get_rule_by_root(root)
            
#             # Initialize patterns with defaults
#             past, mudari, masdar, masdar_mimi, ism_fael, ism_mafool, amr, nahi, zaman, makan, alat = "", "", "", "", "", "", "", "", "", "", ""
            
#             if rule_number == 1:
#                 # Rule 1: فَعَلَ - يَفْعُلُ
#                 past = f"{r1}َ{r2}َ{r3}َ"
#                 mudari = f"يَ{r1}ْ{r2}ُ{r3}ُ"
#                 masdar = f"{r1}َ{r2}ْ{r3}ًا"
#                 masdar_mimi = f"مَ{r1}ْ{r2}َ{r3}ًا"
#                 ism_fael = f"{r1}َا{r2}ِ{r3}ٌ"
#                 ism_mafool = f"مَ{r1}ْ{r2}ُو{r3}ٌ"
#                 amr = f"اُ{r1}ْ{r2}ُ{r3}ْ"
#                 nahi = f"لَا تَ{r1}ْ{r2}ُ{r3}ْ"
#                 zaman = f"مَ{r1}ْ{r2}َ{r3}ٌ"
#                 makan = f"مَ{r1}ْ{r2}َ{r3}ٌ"
#                 alat = f"مِ{r1}ْ{r2}َ{r3}ٌ"
#             elif rule_number == 2:
#                 # Rule 2: فَعَلَ - يَفْعِلُ
#                 past = f"{r1}َ{r2}َ{r3}َ"
#                 mudari = f"يَ{r1}ْ{r2}ِ{r3}ُ"
#                 masdar = f"{r1}َ{r2}ْ{r3}ًا"
#                 masdar_mimi = f"مَ{r1}ْ{r2}َ{r3}ًا"
#                 ism_fael = f"{r1}َا{r2}ِ{r3}ٌ"
#                 ism_mafool = f"مَ{r1}ْ{r2}ُو{r3}ٌ"
#                 amr = f"اِ{r1}ْ{r2}ِ{r3}ْ"
#                 nahi = f"لَا تَ{r1}ْ{r2}ِ{r3}ْ"
#                 zaman = f"مَ{r1}ْ{r2}ِ{r3}ٌ"
#                 makan = f"مَ{r1}ْ{r2}ِ{r3}ٌ"
#                 # The user's rule 2 does not specify a different form for alat. We follow the pattern for "مِفْعَلٌ"
#                 alat = f"مِ{r1}ْ{r2}َ{r3}ٌ"
#             elif rule_number == 3:
#                 # Rule 3: فَعَلَ - يَفْعَلُ
#                 past = f"{r1}َ{r2}َ{r3}َ"
#                 mudari = f"يَ{r1}ْ{r2}َ{r3}ُ"
#                 masdar = f"{r1}َ{r2}ْ{r3}ًا"
#                 masdar_mimi = f"مَ{r1}ْ{r2}َ{r3}ًا"
#                 ism_fael = f"{r1}َا{r2}ِ{r3}ٌ"
#                 ism_mafool = f"مَ{r1}ْ{r2}ُو{r3}ٌ"
#                 amr = f"اِ{r1}ْ{r2}َ{r3}ْ"
#                 nahi = f"لَا تَ{r1}ْ{r2}َ{r3}ْ"
#                 zaman = f"مَ{r1}ْ{r2}َ{r3}ٌ"
#                 makan = f"مَ{r1}ْ{r2}َ{r3}ٌ"
#                 alat = f"مِ{r1}ْ{r2}َا{r3}ٌ"
#             elif rule_number == 4:
#                 # Rule 4: فَعِلَ - يَفْعَلُ
#                 past = f"{r1}َ{r2}ِ{r3}َ"
#                 mudari = f"يَ{r1}ْ{r2}َ{r3}ُ"
#                 masdar = f"{r1}َ{r2}ْ{r3}ًا"
#                 masdar_mimi = f"مَ{r1}ْ{r2}َ{r3}ًا"
#                 ism_fael = f"{r1}َا{r2}ِ{r3}ٌ"
#                 ism_mafool = f"مَ{r1}ْ{r2}ُو{r3}ٌ"
#                 amr = f"اِ{r1}ْ{r2}َ{r3}ْ"
#                 nahi = f"لَا تَ{r1}ْ{r2}َ{r3}ْ"
#                 zaman = f"مَ{r1}ْ{r2}َ{r3}ٌ"
#                 makan = f"مَ{r1}ْ{r2}َ{r3}ٌ"
#                 alat = "TIDAK ADA"
#             elif rule_number == 5:
#                 # Rule 5: فَعُلَ - يَفْعُلُ
#                 past = f"{r1}َ{r2}ُ{r3}َ"
#                 mudari = f"يَ{r1}ْ{r2}ُ{r3}ُ"
#                 masdar = f"{r1}ُ{r2}ْ{r3}ًا"
#                 masdar_mimi = f"مَ{r1}ْ{r2}َ{r3}ًا"
#                 ism_fael = f"{r1}َ{r2}َ{r3}ٌ"
#                 ism_mafool = "TIDAK ADA"
#                 amr = f"اُ{r1}ْ{r2}ُ{r3}ْ"
#                 nahi = f"لَا تَ{r1}ْ{r2}ُ{r3}ْ"
#                 zaman = f"مَ{r1}ْ{r2}َ{r3}ٌ"
#                 makan = f"مَ{r1}ْ{r2}َ{r3}ٌ"
#                 alat = "TIDAK ADA"
#             elif rule_number == 6:
#                 # Rule 6: فَعِلَ - يَفْعِلُ
#                 past = f"{r1}َ{r2}ِ{r3}َ"
#                 mudari = f"يَ{r1}ْ{r2}ِ{r3}ُ"
#                 masdar = f"{r1}ُ{r2}ْ{r3}َانًا"
#                 masdar_mimi = f"مَ{r1}ْ{r2}َ{r3}ًا"
#                 ism_fael = f"{r1}َا{r2}ِ{r3}ٌ"
#                 ism_mafool = f"مَ{r1}ْ{r2}ُو{r3}ٌ"
#                 amr = f"اِ{r1}ْ{r2}ِ{r3}ْ"
#                 nahi = f"لَا تَ{r1}ْ{r2}ِ{r3}ْ"
#                 zaman = f"مَ{r1}ْ{r2}ِ{r3}ٌ"
#                 makan = f"مَ{r1}ْ{r2}ِ{r3}ٌ"
#                 alat = "TIDAK ADA"

#             tasrif_data = [
#                 ("1. الفعل الماضي", past),
#                 ("2. الفعل المضارع", mudari),
#                 ("3. المصدر", masdar),
#                 ("4. المصدر الميمي", masdar_mimi),
#                 ("5. اسم الفاعل", ism_fael),
#                 ("6. اسم المفعول", ism_mafool),
#                 ("7. فعل الأمر", amr),
#                 ("8. فعل النهي", nahi),
#                 ("9. اسم الزمان", zaman),
#                 ("10. اسم المكان", makan),
#                 ("11. اسم الآلة", alat),
#             ]
        
#         elif mode == "lughowiy":
#             # NOTE: For a full solution, this section would also need to be
#             # updated to correctly handle the different vocalizations based on the rule.
#             # This is a simplified example.
#             tasrif_data = [
#                 ("هُوَ", f"{r1}َ{r2}َ{r3}َ"),                    
#                 ("هما (م)", f"{r1}َ{r2}َ{r3}َا"),               
#                 ("هم", f"{r1}َ{r2}َ{r3}ُوا"),                  
#                 ("هي", f"{r1}َ{r2}َ{r3}َتْ"),                  
#                 ("هما (ف)", f"{r1}َ{r2}َ{r3}َتَا"),             
#                 ("هنّ", f"{r1}َ{r2}َ{r3}ْنَ"),                 
#                 ("أنتَ", f"{r1}َ{r2}َ{r3}ْتَ"),                
#                 ("أنتما (م)", f"{r1}َ{r2}َ{r3}ْتُمَا"),        
#                 ("أنتم", f"{r1}َ{r2}َ{r3}ْتُمْ"),              
#                 ("أنتِ", f"{r1}َ{r2}َ{r3}ْتِ"),                
#                 ("أنتما (ف)", f"{r1}َ{r2}َ{r3}ْتُمَا"),        
#                 ("أنتنّ", f"{r1}َ{r2}َ{r3}ْتُنَّ"),            
#                 ("أنا", f"{r1}َ{r2}َ{r3}ْتُ"),                 
#                 ("نحن", f"{r1}َ{r2}َ{r3}ْنَا"),                
#             ]
#         else:
#             return jsonify({"error": "Invalid mode"}), 400

#         return jsonify({"success": True, "tasrif": tasrif_data, "root": root})

#     except Exception as e:
#         return jsonify({"error": f"Server error: {str(e)}"}), 500

# @app.route('/health', methods=['GET'])
# def health_check():
#     return jsonify({"status": "healthy", "message": "Server is running"})

# if __name__ == '__main__':
#     app.run(debug=True, host='0.0.0.0', port=5000)



# ---------------------------------------- V2---------------------------------- 
#  ini sudh hampir selesai
from flask import Flask, request, jsonify
from flask_cors import CORS
import requests
import json
import random
from collections import OrderedDict

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

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
        response = requests.post(url, headers=headers, json=payload)
        response.raise_for_status()
        
        result = response.json()
        
        if 'candidates' in result and len(result['candidates']) > 0:
            content = result['candidates'][0]['content']['parts'][0]['text']
            
            # Try to parse the JSON response
            try:
                # Clean the response if it contains markdown code blocks
                if content.startswith('```json'):
                    content = content.replace('```json', '').replace('```', '').strip()
                elif content.startswith('```'):
                    content = content.replace('```', '').strip()
                
                morphology_data = json.loads(content)
                return morphology_data
            except json.JSONDecodeError:
                # If JSON parsing fails, return the raw content
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
            
    except requests.exceptions.RequestException as e:
        return {
            "error": f"API request failed: {str(e)}",
            "analysis": [],
            "summary": "حدث خطأ في الاتصال بالخدمة"
        }

@app.route('/')
def home():
    return jsonify({"message": "Arabic Morphology API is running!"})

@app.route('/analyze', methods=['POST'])
def analyze_text():
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
        
        # Analyze the text
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
    """
    Determines the Tasrif Istilahi rule (Hukum) for a given root.
    This is a simplified approach for demonstration purposes, mapping
    common roots to their respective rule numbers.
    """
    # Map roots to their rule number based on the provided patterns
    rule_map = {
        'نصر': 1, 'كتب': 1, # Rule 1: فَعَلَ - يَفْعُلُ
        'ضرب': 2, 'جلس': 2, # Rule 2: فَعَلَ - يَفْعِلُ
        'فتح': 3, 'ذهب': 3, # Rule 3: فَعَلَ - يَفْعَلُ
        'علم': 4, 'شرب': 4, # Rule 4: فَعِلَ - يَفْعَلُ
        'كرم': 5, 'حسن': 5, # Rule 5: فَعُلَ - يَفْعُلُ
        'حسب': 6, 'ورث': 6, # Rule 6: فَعِلَ - يَفْعِلُ
    }
    return rule_map.get(root, 1) # Default to rule 1 if root is not found

def generate_tasrif_isim(root):
    """
    Generate different forms of Arabic nouns (singular, dual, plural)
    based on the root letters.
    """
    if len(root) < 3:
        return []
    
    r1, r2, r3 = root[0], root[1], root[2]
    
    # Basic noun patterns - you can expand this with more patterns
    noun_patterns = [
        {
            "pattern_name": "فَاعِل",
            "singular": f"{r1}َا{r2}ِ{r3}ٌ",
            "dual_masculine": f"{r1}َا{r2}ِ{r3}َانِ",
            "dual_feminine": f"{r1}َا{r2}ِ{r3}َتَانِ",
            "plural_masculine": f"{r1}َا{r2}ِ{r3}ُونَ",
            "plural_feminine": f"{r1}َا{r2}ِ{r3}َاتٌ",
            "broken_plural": f"{r1}ُ{r2}َّا{r3}ٌ"
        },
        {
            "pattern_name": "فَعَّال",
            "singular": f"{r1}َ{r2}َّا{r3}ٌ",
            "dual_masculine": f"{r1}َ{r2}َّا{r3}َانِ",
            "dual_feminine": f"{r1}َ{r2}َّا{r3}َتَانِ",
            "plural_masculine": f"{r1}َ{r2}َّا{r3}ُونَ",
            "plural_feminine": f"{r1}َ{r2}َّا{r3}َاتٌ",
            "broken_plural": f"{r1}َ{r2}َّا{r3}ِينَ"
        },
        {
            "pattern_name": "مَفْعُول",
            "singular": f"مَ{r1}ْ{r2}ُو{r3}ٌ",
            "dual_masculine": f"مَ{r1}ْ{r2}ُو{r3}َانِ",
            "dual_feminine": f"مَ{r1}ْ{r2}ُو{r3}َتَانِ",
            "plural_masculine": f"مَ{r1}ْ{r2}ُو{r3}ُونَ",
            "plural_feminine": f"مَ{r1}ْ{r2}ُو{r3}َاتٌ",
            "broken_plural": f"مَ{r1}َا{r2}ِي{r3}ُ"
        }
    ]
    
    # Select the most appropriate pattern (you can make this more sophisticated)
    selected_pattern = noun_patterns[0]  # Default to فَاعِل pattern
    
    tasrif_data = [
        ("المفرد (Singular)", selected_pattern["singular"]),
        ("المثنى المذكر (Dual Masculine)", selected_pattern["dual_masculine"]),
        ("المثنى المؤنث (Dual Feminine)", selected_pattern["dual_feminine"]),
        ("الجمع المذكر السالم (Sound Masculine Plural)", selected_pattern["plural_masculine"]),
        ("الجمع المؤنث السالم (Sound Feminine Plural)", selected_pattern["plural_feminine"]),
        ("جمع التكسير (Broken Plural)", selected_pattern["broken_plural"]),
    ]
    
    return tasrif_data

@app.route('/tasrif', methods=['POST'])
def generate_tasrif():
    try:
        data = request.get_json()
        if not data or 'root' not in data or 'mode' not in data:
            return jsonify({"error": "Need root and mode"}), 400

        # Clean the root input
        root = data['root'].strip().replace(' ', '')
        mode = data['mode']

        if len(root) < 3:
            return jsonify({"error": "Invalid root"}), 400

        r1, r2, r3 = root[0], root[1], root[2]

        if mode == "istilahi":
            # Get the correct rule number for the given root
            rule_number = get_rule_by_root(root)
            
            # Initialize patterns with defaults
            past, mudari, masdar, masdar_mimi, ism_fael, ism_mafool, amr, nahi, zaman, makan, alat = "", "", "", "", "", "", "", "", "", "", ""
            
            if rule_number == 1:
                # Rule 1: فَعَلَ - يَفْعُلُ
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
                # Rule 2: فَعَلَ - يَفْعِلُ
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
                # The user's rule 2 does not specify a different form for alat. We follow the pattern for "مِفْعَلٌ"
                alat = f"مِ{r1}ْ{r2}َ{r3}ٌ"
            elif rule_number == 3:
                # Rule 3: فَعَلَ - يَفْعَلُ
                past = f"{r1}َ{r2}َ{r3}َ"
                mudari = f"يَ{r1}ْ{r2}َ{r3}ُ"
                masdar = f"{r1}َ{r2}ْ{r3}ًا"
                masdar_mimi = f"مَ{r1}ْ{r2}َ{r3}ًا"
                ism_fael = f"{r1}َا{r2}ِ{r3}ٌ"
                ism_mafool = f"مَ{r1}ْ{r2}ُو{r3}ٌ"
                amr = f"اِ{r1}ْ{r2}َ{r3}ْ"
                nahi = f"لَا تَ{r1}ْ{r2}َ{r3}ْ"
                zaman = f"مَ{r1}ْ{r2}َ{r3}ٌ"
                makan = f"مَ{r1}ْ{r2}َ{r3}ٌ"
                alat = f"مِ{r1}ْ{r2}َا{r3}ٌ"
            elif rule_number == 4:
                # Rule 4: فَعِلَ - يَفْعَلُ
                past = f"{r1}َ{r2}ِ{r3}َ"
                mudari = f"يَ{r1}ْ{r2}َ{r3}ُ"
                masdar = f"{r1}َ{r2}ْ{r3}ًا"
                masdar_mimi = f"مَ{r1}ْ{r2}َ{r3}ًا"
                ism_fael = f"{r1}َا{r2}ِ{r3}ٌ"
                ism_mafool = f"مَ{r1}ْ{r2}ُو{r3}ٌ"
                amr = f"اِ{r1}ْ{r2}َ{r3}ْ"
                nahi = f"لَا تَ{r1}ْ{r2}َ{r3}ْ"
                zaman = f"مَ{r1}ْ{r2}َ{r3}ٌ"
                makan = f"مَ{r1}ْ{r2}َ{r3}ٌ"
                alat = "TIDAK ADA"
            elif rule_number == 5:
                # Rule 5: فَعُلَ - يَفْعُلُ
                past = f"{r1}َ{r2}ُ{r3}َ"
                mudari = f"يَ{r1}ْ{r2}ُ{r3}ُ"
                masdar = f"{r1}ُ{r2}ْ{r3}ًا"
                masdar_mimi = f"مَ{r1}ْ{r2}َ{r3}ًا"
                ism_fael = f"{r1}َ{r2}َ{r3}ٌ"
                ism_mafool = "TIDAK ADA"
                amr = f"اُ{r1}ْ{r2}ُ{r3}ْ"
                nahi = f"لَا تَ{r1}ْ{r2}ُ{r3}ْ"
                zaman = f"مَ{r1}ْ{r2}َ{r3}ٌ"
                makan = f"مَ{r1}ْ{r2}َ{r3}ٌ"
                alat = "TIDAK ADA"
            elif rule_number == 6:
                # Rule 6: فَعِلَ - يَفْعِلُ
                past = f"{r1}َ{r2}ِ{r3}َ"
                mudari = f"يَ{r1}ْ{r2}ِ{r3}ُ"
                masdar = f"{r1}ُ{r2}ْ{r3}َانًا"
                masdar_mimi = f"مَ{r1}ْ{r2}َ{r3}ًا"
                ism_fael = f"{r1}َا{r2}ِ{r3}ٌ"
                ism_mafool = f"مَ{r1}ْ{r2}ُو{r3}ٌ"
                amr = f"اِ{r1}ْ{r2}ِ{r3}ْ"
                nahi = f"لَا تَ{r1}ْ{r2}ِ{r3}ْ"
                zaman = f"مَ{r1}ْ{r2}ِ{r3}ٌ"
                makan = f"مَ{r1}ْ{r2}ِ{r3}ٌ"
                alat = "TIDAK ADA"

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
            # NOTE: For a full solution, this section would also need to be
            # updated to correctly handle the different vocalizations based on the rule.
            # This is a simplified example.
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
            # Generate noun conjugations (singular, dual, plural)
            tasrif_data = generate_tasrif_isim(root)
        
        else:
            return jsonify({"error": "Invalid mode"}), 400

        return jsonify({"success": True, "tasrif": tasrif_data, "root": root})

    except Exception as e:
        return jsonify({"error": f"Server error: {str(e)}"}), 500

@app.route('/health', methods=['GET'])
def health_check():
    return jsonify({"status": "healthy", "message": "Server is running"})

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)