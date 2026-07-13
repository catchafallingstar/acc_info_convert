import os
import io
import json
import base64
import requests
import markdown
from django.http import JsonResponse, HttpResponse
from django.views.decorators.csrf import csrf_exempt
from weasyprint import HTML
import fitz
import pypdf 
from pypdf import PdfWriter, PdfReader
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
            "and does NOT look like a flowchart, timeline, or infographic, respond with EXACTLY this phrase: 'VALIDATION_ERROR: Not a structured infographic.' "
            "Otherwise, rebuild it into a logical, sequential text narrative for screen readers. "
            "YOU MUST USE STRICT MARKDOWN SYNTAX. Use '#' for main headings, '##' for subheadings, and '*' or '-' for bullet points. "
            "Do NOT use unicode bullet symbols (•) or plain text numbering for headers. Do not include introductory filler."
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
    if request.method != 'POST':
        return HttpResponse(status=405)

    try:
        data = json.loads(request.body)
        narrative = data.get('narrative', '')
        base64_file = data.get('image', '')

        # 1. Convert the raw Markdown text from the AI into actual HTML tags!
        narrative_html = markdown.markdown(narrative)

        is_pdf_upload = base64_file.startswith('data:application/pdf')

        # 2. Determine the image source for the HTML
        image_src = ""
        
        if is_pdf_upload:
            # If it's a PDF, extract bytes, render the first page as an image, and convert to base64 PNG
            header, encoded_string = base64_file.split(',', 1)
            pdf_bytes = base64.b64decode(encoded_string)
            
            # Open PDF with PyMuPDF and grab the first page
            pdf_document = fitz.open(stream=pdf_bytes, filetype="pdf")
            first_page = pdf_document.load_page(0)
            
            # Render page to a high-quality image (dpi=150)
            pix = first_page.get_pixmap(dpi=150)
            png_bytes = pix.tobytes("png")
            
            # Re-encode as a PNG base64 string
            encoded_png = base64.b64encode(png_bytes).decode('utf-8')
            image_src = f"data:image/png;base64,{encoded_png}"
        else:
            # If it's already an image, use it directly
            image_src = base64_file

        # 3. Setup the HTML structure
        html_content = f"""
        <div style="font-family: sans-serif; padding: 20px;">
            <h1 style="color: #007bff;">Accessible Description</h1>
            <div style="font-size: 14px; line-height: 1.6;">
                {narrative_html}
            </div>
        """

        # 4. Embed the image (whether originally an image or converted from a PDF)
        if image_src:
            html_content += f"""
            <hr style="margin: 40px 0;">
            <h2>Original Infographic Source</h2>
            <!-- The 'alt' tag here is crucial for screen readers -->
            <img src="{image_src}" alt="Original infographic document" style="max-width: 100%; border: 1px solid #ccc;">
            """
        
        html_content += "</div>"

        # 5. Generate the final PDF in one pass with WeasyPrint (Tags included!)
        final_pdf_bytes = HTML(string=html_content).write_pdf(
            pdf_variant="pdf/ua-1", 
            pdf_tags=True
        )

        # 6. Send the final compiled PDF back to the user's browser
        response = HttpResponse(final_pdf_bytes, content_type='application/pdf')
        response['Content-Disposition'] = 'attachment; filename="Accessible_Narrative.pdf"'
        return response

    except Exception as e:
        print(f"Error generating PDF: {e}")
        return HttpResponse("Server error while generating PDF", status=500)
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
            "You are an expert Web Accessibility specialist. Analyze the following raw text extracted from an image or PDF. "
            "CRITICAL CHECK: If the text is random unreadable garbage, or if it is clearly just a standard block of text "
            "and does NOT look like a flowchart, timeline, or infographic, respond with EXACTLY this phrase: 'VALIDATION_ERROR: Not a structured infographic.' "
            "Otherwise, rebuild it into a logical, sequential text narrative for screen readers. "
            "YOU MUST USE STRICT MARKDOWN SYNTAX. Use '#' for main headings, '##' for subheadings, and '*' or '-' for bullet points. "
            "Do NOT use unicode bullet symbols (•) or plain text numbering for headers. Do not include introductory filler."
        )
        full_prompt = f"{system_prompt}\n\nConvert this raw text now:\n\"{extracted_text}\""
        
        # 5. Make the secure server-to-server request
        url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent?key={gemini_api_key}"
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
