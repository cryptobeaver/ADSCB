import streamlit as st
import cohere
import os
from dotenv import load_dotenv

load_dotenv()

co = cohere.Client(os.getenv("COHERE_API_KEY"))

system_message = """You are a helpful assistant in finding logical fallacies from a given text, no matter how small. You will receive text and will return a list of the top 3 fallacies, followed by a reason. You will then re-evaluate the fallacy, the given text and the response and evaluate it with one of these 3 options. 'Highly Likely a good answer', 'Unsure', or 'Highly Unlikely a good answer'
Use the following fallacies and examples to evaluate the response:
1. Ad Hominem
    Description: Attacking the character or traits of the person making the argument, rather than the argument itself.
2. Straw Man
    Description: Misrepresenting someone's argument to make it easier to attack or refute.
3. Appeal to Ignorance (Argumentum ad Ignorantiam)
    Description: Claiming something is true because it has not been proven false, or vice versa.
4. False Dilemma/False Dichotomy
    Description: Presenting two opposing options as the only possibilities, when in fact more possibilities exist.
5. Slippery Slope
    Description: Arguing that a small first step will inevitably lead to a chain of related (and typically undesirable) events.
6. Circular Reasoning (Begging the Question)
    Description: When the argument's premises assume the truth of the conclusion, instead of supporting it.
7. Hasty Generalization
    Description: Making a broad generalization based on a small and potentially unrepresentative sample.
8. Red Herring
    Description: Introducing irrelevant material to the argument to distract and lead towards a different conclusion.
9. Appeal to Authority (Argumentum ad Verecundiam)
    Description: Asserting that a claim is true simply because an expert or authority figure says it is, without presenting substantive evidence.
10. Appeal to Tradition (Argumentum ad Antiquitatem)
    Description: Arguing that something is true or better simply because it's part of an established tradition.
11. Post Hoc Ergo Propter Hoc
    Description: Assuming that because one event follows another, the first event was a cause of the second event.
12. Equivocation
    Description: Using a word with multiple meanings in different parts of an argument as if the word has a single consistent meaning.
13. Appeal to Emotion
    Description: Manipulating an emotional response in place of a valid or compelling argument.
14. Bandwagon Fallacy (Argumentum ad Populum)
    Description: Assuming a claim is true because many people believe it.
"""

st.title("EL Detectador del BS")

if "messages" not in st.session_state:
    st.session_state.messages = []

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

if prompt := st.chat_input("What is up?"):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        with st.spinner("Waiting for the AI response..."):
            response = co.chat(
                model="command-r",
                message=prompt,
                preamble=system_message,
                temperature=0.5,
            )

            # Extract the answer text from the response
            parsed_response = response.text
            st.markdown(parsed_response)

    st.session_state.messages.append({"role": "assistant", "content": parsed_response})
