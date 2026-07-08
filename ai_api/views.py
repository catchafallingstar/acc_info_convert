import os
import json
import requests
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt

@csrf_exempt  # Allows your React frontend to POST data to this endpoint
def process_ai(request):
    if request.method != 'POST':
        return JsonResponse({'error': 'Only POST requests allowed'}, status=405)
        
    try:
        # 1. Parse the text sent from your React frontend
        body = json.loads(request.body)
        raw_text = body.get('raw_text', '')

        if not raw_text.strip():
            return JsonResponse({'error': 'No text provided'}, status=400)

        # 2. Grab your token securely from the server environment
        gemini_api_key = os.environ.get('GEMINI_API_KEY')
        if not gemini_api_key:
            return JsonResponse({'error': 'Server configuration error: Gemini API Key missing'}, status=500)

        # 3. Setup the AI model prompt layout
        system_prompt = (
            "You are an expert Web Accessibility specialist. Take the following messy raw text "
            "extracted from a flowchart/infographic and rebuild it into a logical, sequential text narrative "
            "for screen readers. Use clean markdown headings, chronological steps, and detailed bullet points."
        )
        full_prompt = f"{system_prompt}\n\nConvert this raw text now:\n\"{raw_text}\""
        # 4. Make the secure server-to-server request
        url =f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent?key={gemini_api_key}"
        headers = {
            "Authorization": f"Bearer {gemini_api_key}",
            "Content-Type": "application/json"
        }
        payload = {
            "contents": [
                {
                    "parts": [{"text": full_prompt}]
                }
            ]
        }


        response = requests.post(url, headers=headers, json=payload)


        ai_response_data = response.json()


        # 5. Extract the generated text safely from Gemini
        if response.status_code == 200:
            try:
                generated_text = ai_response_data['candidates'][0]['content']['parts'][0]['text']
                return JsonResponse({'generated_text': generated_text})
            except (KeyError, IndexError):
                return JsonResponse({'error': 'Failed to parse Gemini response', 'details': ai_response_data}, status=500)
        else:

            return JsonResponse({
                'error': 'Gemini API Error',
                'status_code': response.status_code,
                'details': ai_response_data
            }, status=500)


    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)