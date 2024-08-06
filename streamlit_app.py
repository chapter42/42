import streamlit as st
from openai import OpenAI
from typing import List
import toml

# Functie om de API-sleutel uit het TOML-bestand te lezen
def read_api_key_from_toml():
    try:
        config = toml.load('.streamlit/secrets.toml')
        return config.get('OPENAI_API_KEY')
    except FileNotFoundError:
        return None
    except toml.TomlDecodeError:
        st.error("Fout bij het decoderen van het TOML-bestand.")
        return None

# Vooraf gedefinieerde prompts
DEFAULT_PROMPTS = [
    "Geef een samenvatting van de belangrijkste punten in deze tekst.",
    "Identificeer de hoofdthema's en geef een korte uitleg bij elk thema.",
    "Stel drie kritische vragen over de inhoud van deze tekst."
]

# Beschikbare GPT-modellen
GPT_MODELS = [
    "gpt-4o",
    "gpt-4o-mini",
    "gpt-4-1106-preview"
]

# Functie om ChatGPT aan te roepen
def call_chatgpt(prompt: str, client: OpenAI, model: str) -> str:
    try:
        completion = client.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": "Je bent een behulpzame assistent die teksten analyseert en samenvat."},
                {"role": "user", "content": prompt}
            ]
        )
        return completion.choices[0].message.content
    except Exception as e:
        return f"Error bij het aanroepen van {model}: {str(e)}"

# Functie om meerdere prompts te verwerken
def process_prompts(text: str, prompts: List[str], client: OpenAI, model: str) -> List[str]:
    results = []
    for prompt in prompts:
        full_prompt = f"{prompt}\n\nText: {text}"
        result = call_chatgpt(full_prompt, client, model)
        results.append(result)
    return results

# Streamlit app
def main():
    st.set_page_config(layout="wide")
    
    # Titel
    st.title("Markdown Input en GPT Output")
    
    # Initialiseer sessie state voor markdown input en prompts
    if 'markdown_input' not in st.session_state:
        st.session_state.markdown_input = ""
    if 'prompts' not in st.session_state:
        st.session_state.prompts = DEFAULT_PROMPTS.copy()
    
    # Lees de API-sleutel uit het TOML-bestand
    toml_api_key = read_api_key_from_toml()
    
    # Twee kolommen: links voor input, rechts voor output
    col1, col2 = st.columns([1, 1])
    
    with col1:
        # Markdown invoerveld
        st.session_state.markdown_input = st.text_area("Voer uw markdown tekst in:", value=st.session_state.markdown_input, height=300)
        
        # API key input (alleen als er geen TOML-sleutel is)
        if not toml_api_key:
            api_key = st.text_input("Voer uw OpenAI API key in:", type="password")
        else:
            api_key = toml_api_key
            st.success("API-sleutel succesvol geladen uit configuratie.")
        
        # Model selectie
        selected_model = st.selectbox("Kies een GPT model:", GPT_MODELS)
        
        # Toon en bewerk prompts
        st.subheader("Prompts (bewerk indien nodig):")
        for i in range(len(st.session_state.prompts)):
            st.session_state.prompts[i] = st.text_area(f"Prompt {i+1}:", value=st.session_state.prompts[i], height=100, key=f"prompt_{i}")
        
        # Verwerk knop
        if st.button("Verwerk"):
            if not api_key:
                st.error("Er is geen geldige API-sleutel gevonden. Voer een API-sleutel in of configureer deze in het TOML-bestand.")
            elif not st.session_state.markdown_input:
                st.error("Voer alstublieft een markdown tekst in.")
            else:
                with st.spinner("Bezig met verwerken..."):
                    client = OpenAI(api_key=api_key)
                    results = process_prompts(st.session_state.markdown_input, st.session_state.prompts, client, selected_model)
                    
                    # Toon resultaten in de rechterkolom
                    with col2:
                        for i, result in enumerate(results):
                            st.subheader(f"Resultaat voor Prompt {i+1}")
                            st.markdown(result)

if __name__ == "__main__":
    main()