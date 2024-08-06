import streamlit as st
import openai
from typing import List

# Vooraf gedefinieerde prompts
PROMPTS = [
    "Geef een samenvatting van de belangrijkste punten in deze tekst.",
    "Identificeer de hoofdthema's en geef een korte uitleg bij elk thema.",
    "Stel drie kritische vragen over de inhoud van deze tekst."
]

# Beschikbare GPT-modellen
GPT_MODELS = {
    "GPT-4o": "GPT-4o",
    "GPT-4o mini": "GPT-4o mini",
    "GPT-4 Turbo": "gpt-4-1106-preview"
}

# Functie om ChatGPT aan te roepen
def call_chatgpt(prompt: str, api_key: str, model: str) -> str:
    openai.api_key = api_key
    try:
        response = openai.ChatCompletion.create(
            model=model,
            messages=[{"role": "user", "content": prompt}]
        )
        return response.choices[0].message.content
    except Exception as e:
        return f"Error: {str(e)}"

# Functie om meerdere prompts te verwerken
def process_prompts(text: str, prompts: List[str], api_key: str, model: str) -> List[str]:
    results = []
    for prompt in prompts:
        full_prompt = f"{prompt}\n\nText: {text}"
        result = call_chatgpt(full_prompt, api_key, model)
        results.append(result)
    return results

# Streamlit app
def main():
    st.set_page_config(layout="wide")
    
    # Titel
    st.title("Markdown Input en GPT Output")
    
    # Twee kolommen: links voor input, rechts voor output
    col1, col2 = st.columns([1, 1])
    
    with col1:
        # Markdown invoerveld
        markdown_input = st.text_area("Voer uw markdown tekst in:", height=300)
        
        # API key input
        api_key = st.text_input("Voer uw OpenAI API key in:", type="password")
        
        # Model selectie
        selected_model = st.selectbox("Kies een GPT model:", list(GPT_MODELS.keys()))
        
        # Toon en bewerk prompts
        st.subheader("Prompts (bewerk indien nodig):")
        edited_prompts = []
        for i, prompt in enumerate(PROMPTS):
            edited_prompt = st.text_area(f"Prompt {i+1}:", value=prompt, height=100)
            edited_prompts.append(edited_prompt)
        
        # Verwerk knop
        if st.button("Verwerk"):
            if not api_key:
                st.error("Voer alstublieft uw OpenAI API key in.")
            elif not markdown_input:
                st.error("Voer alstublieft een markdown tekst in.")
            else:
                with st.spinner("Bezig met verwerken..."):
                    results = process_prompts(markdown_input, edited_prompts, api_key, GPT_MODELS[selected_model])
                    
                    # Toon resultaten in de rechterkolom
                    with col2:
                        for i, result in enumerate(results):
                            st.subheader(f"Resultaat voor Prompt {i+1}")
                            st.markdown(result)

if __name__ == "__main__":
    main()