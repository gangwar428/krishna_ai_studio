import re, json

def analyze_with_gemini(client, image_pill):
    try:
        # Strict prompt to prevent "Modern/Neutral" copy-paste
        prompt = """Analyze this bathmat image. 
        Identify specific 'Style' (e.g. Spooky Halloween, Checkered Braided, Embossed Floral) 
        and 'Color' (e.g. Terracotta, Charcoal, Ivory).
        Return ONLY JSON: {"Product": "Bathmat", "Style": "style_name", "Color": "color_name", "Size": "50x80 cm", "Material": "Textile"}"""
        
        response = client.models.generate_content(model="gemini-1.5-flash", contents=[prompt, image_pill])
        clean_json = re.search(r'\{.*\}', response.text, re.DOTALL).group()
        return json.loads(clean_json)
    except:
        return {"Product": "Bathmat", "Style": "Textured", "Color": "Multi-Tone", "Size": "50x80 cm", "Material": "Textile"}
