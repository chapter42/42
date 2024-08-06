import streamlit as st
from openai import OpenAI
import requests
from typing import List, Dict
import toml
import os

# Functie om de API-sleutel uit het TOML-bestand te lezen
def read_api_key_from_toml():
    try:
        config = toml.load('.streamlit/secrets.toml')
        return config.get('API_key')
    except FileNotFoundError:
        return None
    except toml.TomlDecodeError:
        st.error("Fout bij het decoderen van het TOML-bestand.")
        return None

# Vooraf gedefinieerde prompts
PROMPTS = [
    "Geef een samenvatting van de belangrijkste punten in deze tekst.",
    "Identificeer de hoofdthema's en geef een korte uitleg bij elk thema.",
    "Stel drie kritische vragen over de inhoud van deze tekst."
]

# Beschikbare GPT-modellen en hun API-endpoints
GPT_MODELS: Dict[str, Dict[str, str]] = {
    "GPT-4o": {"name": "GPT-4o", "api": ""},
    "GPT-4o mini": {"name": "GPT-4o mini", "api": ""},
    "GPT-4 Turbo": {"name": "gpt-4-1106-preview", "api": "https://api.openai.com/v1/chat/completions"}
}

# Functie om GPT-4o en GPT-4o mini aan te roepen
def call_custom_gpt(prompt: str, model: Dict[str, str], api_key: str) -> str:
    if not model['api']:
        return f"Error: API endpoint voor {model['name']} is niet geconfigureerd."
    
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    data = {
        "model": model['name'],
        "prompt": prompt,
        "max_tokens": 150
    }
    try:
        response = requests.post(model['api'], headers=headers, json=data)
        response.raise_for_status()
        return response.json()['choices'][0]['text']
    except requests.RequestException as e:
        return f"Error bij het aanroepen van {model['name']}: {str(e)}"

# Functie om ChatGPT aan te roepen
def call_chatgpt(prompt: str, client: OpenAI, model: Dict[str, str], api_key: str) -> str:
    try:
        if model['name'] in ["GPT-4o", "GPT-4o mini"]:
            return call_custom_gpt(prompt, model, api_key)
        else:
            response = client.chat.completions.create(
                model=model['name'],
                messages=[{"role": "user", "content": prompt}]
            )
            return response.choices[0].message.content
    except Exception as e:
        return f"Error bij het aanroepen van {model['name']}: {str(e)}"

# Functie om meerdere prompts te verwerken
def process_prompts(text: str, prompts: List[str], client: OpenAI, model: Dict[str, str], api_key: str) -> List[str]:
    results = []
    for prompt in prompts:
        full_prompt = f"{prompt}\n\nText: {text}"
        result = call_chatgpt(full_prompt, client, model, api_key)
        results.append(result)
    return results

# Streamlit app
def main():
    st.set_page_config(layout="wide")
    
    # Titel
    st.title("Markdown Input en GPT Output")
    
    # Lees de API-sleutel uit het TOML-bestand
    toml_api_key = read_api_key_from_toml()
    
    # Twee kolommen: links voor input, rechts voor output
    col1, col2 = st.columns([1, 1])
    
    with col1:
        # Markdown invoerveld
        markdown_input = st.text_area("Voer uw markdown tekst in:", height=300)
        
        # API key input
        api_key = st.text_input("Voer uw API key in:", type="password", value=toml_api_key or "")
        
        # Model selectie
        selected_model = st.selectbox("Kies een GPT model:", list(GPT_MODELS.keys()))
        
        # API endpoint configuratie
        if selected_model in ["GPT-4o", "GPT-4o mini"]:
            GPT_MODELS[selected_model]["api"] = st.text_input(f"API endpoint voor {selected_model}:", value=GPT_MODELS[selected_model]["api"])
        
        # Toon en bewerk prompts
        st.subheader("Prompts (bewerk indien nodig):")
        edited_prompts = []
        for i, prompt in enumerate(PROMPTS):
            edited_prompt = st.text_area(f"Prompt {i+1}:", value=prompt, height=100)
            edited_prompts.append(edited_prompt)
        
        # Verwerk knop
        if st.button("Verwerk"):
            if not api_key:
                st.error("Voer alstublieft uw API key in of configureer deze in het TOML-bestand.")
            elif not markdown_input:
                st.error("Voer alstublieft een markdown tekst in.")
            elif selected_model in ["GPT-4o", "GPT-4o mini"] and not GPT_MODELS[selected_model]["api"]:
                st.error(f"Voer alstublieft een API endpoint in voor {selected_model}.")
            else:
                with st.spinner("Bezig met verwerken..."):
                    client = OpenAI(api_key=api_key)
                    results = process_prompts(markdown_input, edited_prompts, client, GPT_MODELS[selected_model], api_key)
                    
                    # Toon resultaten in de rechterkolom
                    with col2:
                        for i, result in enumerate(results):
                            st.subheader(f"Resultaat voor Prompt {i+1}")
                            st.markdown(result)

if __name__ == "__main__":
    main()