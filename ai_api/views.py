import os
import json
import requests
import markdown
from django.http import JsonResponse, HttpResponse
from django.views.decorators.csrf import csrf_exempt
from weasyprint import HTML
import pypdf

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
                         "You are an expert Web Accessibility specialist. Analyze the following raw text extracted from an image. "
                        "CRITICAL CHECK: If the text is random unreadable garbage, or if it is clearly just a standard block of text "
                        "(like a book chapter or grocery list) and does NOT look like it came from a flowchart, timeline, diagram, "
                        "or infographic, respond with EXACTLY this phrase: 'VALIDATION_ERROR: Not a structured infographic.' "
                        "Otherwise, proceed to rebuild it into a logical, sequential text narrative for screen readers. "
                        "Use clean markdown headings, chronological steps, and detailed bullet points. Do not include introductory filler."
        )
        full_prompt = f"{system_prompt}\n\nConvert this raw text now:\n\"{raw_text}\""
        # 4. Make the secure server-to-server request
        url =f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent?key={gemini_api_key}"
        headers = {
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


# ==========================================
# 2. THE ACCESSIBLE PDF GENERATOR ENDPOINT
# ==========================================
@csrf_exempt
def generate_accessible_pdf(request):
    if request.method == 'POST':
        # Parse the incoming data from React
        data = json.loads(request.body)
        narrative_text = data.get('narrative', '')
        image_data = data.get('image', '')  # This should be your base64 image string

        # Convert Gemini's Markdown text into Semantic HTML (<p>, <h2>, <ul>)
        html_content = markdown.markdown(narrative_text)

        # Build a complete HTML document with accessibility attributes
        full_html = f"""
        <!DOCTYPE html>
        <html lang="en">
        <head>
            <meta charset="UTF-8">
            <title>Accessible Image Description</title>
            <style>
                body {{ font-family: Helvetica, Arial, sans-serif; line-height: 1.6; padding: 2cm; }}
                h1 {{ font-size: 24px; border-bottom: 2px solid #333; padding-bottom: 10px; }}
                h2 {{ font-size: 20px; margin-top: 24px; }}
                h3 {{ font-size: 16px; margin-top: 20px; }}
                p, li {{ font-size: 12px; }}
                /* Force the image to start on a brand new page */
                .image-container {{ page-break-before: always; margin-top: 2cm; }}
                img {{ max-width: 100%; height: auto; }}
            </style>
        </head>
        <body>
            <h1>Accessible Image Description</h1>
            {html_content}
        """

        # Safely append the original image as an accessible <figure>
        if image_data:
            full_html += f"""
            <div class="image-container">
                <h2>Original Infographic Source</h2>
                <hr>
                <br>
                <img src="{image_data}" alt="Original uploaded infographic chart">
            </div>
            """

        full_html += """
        </body>
        </html>
        """

        # Compile the HTML into a Tagged PDF using the Universal Accessibility (UA) standard
        pdf_file = HTML(string=full_html).write_pdf(
            pdf_variant="pdf/ua-1"
        )

        # Send the PDF file back to the browser
        response = HttpResponse(pdf_file, content_type='application/pdf')
        response['Content-Disposition'] = 'attachment; filename="Accessible_Narrative.pdf"'
        
        return response

    return HttpResponse(status=405) # Method Not Allowed

# ==========================================
# 3. THE NEW PDF PROCESSING ENDPOINT
# ==========================================
@csrf_exempt
def process_pdf_ai(request):
    if request.method != 'POST':
        return JsonResponse({'error': 'Only POST requests allowed'}, status=405)
        
    try:
        # 1. Catch the uploaded PDF file from React
        if 'file' not in request.FILES:
            return JsonResponse({'error': 'No file uploaded'}, status=400)
            
        pdf_file = request.FILES['file']

        # 2. Extract text from all pages of the PDF
        extracted_text = ""
        reader = pypdf.PdfReader(pdf_file)
        for page in reader.pages:
            text = page.extract_text()
            if text:
                extracted_text += text + "\n"

        if not extracted_text.strip():
            return JsonResponse({'error': 'No readable text found. This might be a flattened image saved as a PDF.'}, status=400)

        # 3. Grab your token securely
        gemini_api_key = os.environ.get('GEMINI_API_KEY')
        if not gemini_api_key:
            return JsonResponse({'error': 'Server configuration error'}, status=500)

        # 4. Setup the AI model prompt layout (reusing your existing accessibility prompt)
        system_prompt = ( 
            "You are an expert Web Accessibility specialist. Analyze the following raw text extracted from a PDF. "
            "CRITICAL CHECK: If the text is random unreadable garbage, or if it is clearly just a standard block of text "
            "(like a book chapter or grocery list) and does NOT look like it came from a flowchart, timeline, diagram, "
            "or infographic, respond with EXACTLY this phrase: 'VALIDATION_ERROR: Not a structured infographic.' "
            "Otherwise, proceed to rebuild it into a logical, sequential text narrative for screen readers. "
            "Use clean markdown headings, chronological steps, and detailed bullet points. Do not include introductory filler."
        )
        full_prompt = f"{system_prompt}\n\nConvert this raw text now:\n\"{extracted_text}\""
        
        # 5. Make the secure server-to-server request
        url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={gemini_api_key}"
        headers = {
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

        # 6. Extract the generated text safely from Gemini
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