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
        hf_token = os.environ.get('VITE_HF_TOKEN')
        if not hf_token:
            return JsonResponse({'error': 'Server configuration error: Token missing'}, status=500)

        # 3. Setup the AI model prompt layout
        system_prompt = (
            "You are an expert Web Accessibility specialist. Take the following messy raw text "
            "extracted from a flowchart/infographic and rebuild it into a logical, sequential text narrative "
            "for screen readers. Use clean markdown headings, chronological steps, and detailed bullet points."
        )

        # 4. Make the secure server-to-server request
        url = "https://api-inference.huggingface.co/models/meta-llama/Meta-Llama-3-8B-Instruct"
        headers = {
            "Authorization": f"Bearer {hf_token}",
            "Content-Type": "application/json"
        }
        payload = {
            "inputs": f"<|system|>\n{system_prompt}\n<|user|>\nConvert this raw text now:\n\"{raw_text}\"\n<|assistant|>\n",
            "parameters": {"max_new_tokens": 800, "return_full_text": False}
        }

        response = requests.post(url, headers=headers, json=payload)
        ai_response_data = response.json()

        # 5. Extract the generated text safely
        if isinstance(ai_response_data, list) and len(ai_response_data) > 0:
            generated_text = ai_response_data[0].get('generated_text', 'No response generated.')
            return JsonResponse({'generated_text': generated_text})
        else:
            return JsonResponse({'error': 'AI Model error or rate limit hit'}, status=500)

    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)