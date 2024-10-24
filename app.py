import streamlit as st
import pandas as pd
from sentence_transformers import SentenceTransformer
from pinecone import Pinecone

import os
from dotenv import load_dotenv, find_dotenv

load_dotenv()

# Cargar el DataFrame
df = pd.read_csv("data/clean_data/series.csv")  

# Inicializa el modelo de embeddings
model = SentenceTransformer('all-MiniLM-L6-v2')  

# Conecta a Pinecone
API_key = os.getenv("key")
pc = Pinecone(api_key=API_key)  
index = pc.Index('series')  



# Función de búsqueda
def search_series(query, search_type, min_rating):
    if search_type == 'Synopsis':
        # Genera un vector para la consulta
        vector = model.encode(query).tolist()
        # Realiza la búsqueda en Pinecone usando argumentos nombrados
        results = index.query(vector=vector, top_k=10, include_values=True)
        # Obtiene los IDs y valores de los resultados
        recommended_series = []
        for match in results['matches']:
            series_id = match['id']
            score = match['score']
            # Busca en el DataFrame original para obtener más información sobre la serie
            series_info = df[df['IMDb ID'] == series_id].iloc[0]  
            # Filtrar series con al menos 1000 valoraciones
            if series_info['Number of Votes'] >= 1000 and series_info['Rating'] >= min_rating:
                recommended_series.append({
                    'Title': series_info['Title'],
                    'Genre': series_info['Genre'],
                    'Cast': series_info['Cast'],
                    'Synopsis': series_info['Synopsis'],  
                    'Rating': series_info['Rating'],
                    'Score': score
                })
        return recommended_series

    # Lógica para buscar por título o autor (en este caso, autor se cambiará a 'Cast')
    elif search_type == 'Title':
        return df[df['Title'].str.contains(query, case=False)& (df['Rating'] >= min_rating)].to_dict('records')
    elif search_type == 'Cast':
        return df[df['Cast'].str.contains(query, case=False)& (df['Rating'] >= min_rating)].to_dict('records')




# Función para obtener las 10 mejores series por género
def get_top_series_by_genre_and_subgenre(genre, subgenres, n=10):
    filtered_series = df[df['Genre'].str.contains(genre, case=False)].drop_duplicates()
    
    if subgenres: 
        filtered_series = filtered_series[filtered_series['Genre'].str.contains('|'.join(subgenres), case=False)]
    filtered_series = filtered_series[filtered_series['Number of Votes'] >= 10000]
    top_series = filtered_series.nlargest(n, 'Rating')
    return top_series.to_dict('records')

# Función para obtener la historia de la empresa
import streamlit as st

import streamlit as st

def get_company_history():
    # Título
    st.markdown("### Bienvenido a nuestra plataforma de recomendación de series, un proyecto de la **Fundación HC Bank**.")
    
    # Explicación sobre la Fundación HC Bank
    st.markdown("""
    La **Fundación HC Bank** es una iniciativa del **HC Bank** que busca fomentar el acceso a la cultura y el entretenimiento para personas de todas las edades. 
    Nació con el propósito de difundir la cultura y conectar generaciones a través de diversas formas de expresión artística, 
    utilizando la tecnología para llevar el contenido cultural de una manera innovadora y accesible.
    """)
    
    # Mostrar el logo centrado
    st.markdown('<div style="text-align: center;"><img src="resources/logo_hcbank.jpeg" alt="HC Bank Logo" width="200"></div>', unsafe_allow_html=True)

    # Resto del texto
    st.markdown("""
    Este proyecto nace en 2024 como parte de nuestro compromiso con la difusión cultural, utilizando la tecnología más avanzada para ofrecer una experiencia única. 
    A través de nuestra plataforma, queremos facilitar el descubrimiento de contenido audiovisual de calidad, adaptado a los gustos y emociones de cada usuario.

    Con la ayuda de la inteligencia artificial y herramientas de recomendación, nuestra app te sugiere contenido basado en tus preferencias, para que disfrutes de nuevas joyas y expandas tus horizontes culturales. 
    ¡Gracias por unirte a nosotros en este viaje cultural! Esperamos que encuentres tu próxima serie favorita.
    """)




# Interfaz de usuario en Streamlit
st.title("🛋️🎉 Aventuras en el Sofá: ¡Maratones Épicos! 🍿🎬")
# Agregar una imagen en la barra lateral
st.sidebar.image("resources/princess_photo.jpeg", caption="🎬Your next adventure in entertainment starts here!🍿", use_column_width=True)
# Navegación de páginas
page = st.sidebar.radio("Select a page", ["Our Story", "Top 10", "Moods", "Recommender"])

st.sidebar.markdown("<br>" * 2, unsafe_allow_html=True)
# Agregar una imagen en la barra lateral
logo_url = "resources/logo_hcbank.jpeg"
st.sidebar.image(logo_url, width=100)

if page == "Recommender":
    st.markdown("""
    ### Recommender
    Looking for a specific series? 
    Use our search tool to find titles, cast members, or synopses. 
    Filter results by rating to discover the best shows that match your query!
    """)
    search_type = st.selectbox("Select search type", ["Title", "Cast", "Synopsis"])
    query = st.text_input("Please enter your search:")
    rating_filter = st.slider("Minimum Rating", 0.0, 10.0, 5.0)
    if st.button("Search"):
        if query:
            if search_type == "Synopsis":
                results = search_series(query, search_type, rating_filter)
                
                for series in results:
                    st.write(f"**✨{series['Title']}✨**")
                    st.write(f"🎭 Genre: {series['Genre']}")
                    st.write(f"🎥 Cast: {series['Cast']}")
                    st.write(f"⭐️ Rating: {series['Rating']}")
                    st.write(f"**🎬 Synopsis:** {series['Synopsis']}")
                    st.markdown("---")
            else:
                results = search_series(query, search_type, rating_filter)
               
                for series in results:
                    st.write(f"**✨{series['Title']}✨**")  # Título de la serie
                    st.write(f"🎭 Genre: {series['Genre']}")  # Género de la serie
                    st.write(f"🎥 Cast: {series['Cast']}")  # Reparto de la serie
                    st.write(f"⭐️ Rating: {series['Rating']}")
                    st.write(f"**🎬 Synopsis:** {series['Synopsis']}")  # Sinopsis de la serie
                    st.markdown("---")
        else:
            st.warning("Please enter a search term.")
elif page == "Top 10":
    st.markdown("""
    ### Top 10 Series
    Discover the best series according to your preferences! 
    You can select a main genre and even choose subgenres to narrow down your options. 
    Our top-rated recommendations will help you find the most acclaimed shows to watch.
    """)
    # Seleccionar un género principal
    genre = st.selectbox("Select a gendre", df['Main Genre'].unique())
    # Seleccionar subgéneros (puede seleccionar múltiples)
    subgenres = st.multiselect("Do you want to choose a subgenre?", df['Genre'].str.split(',').explode().unique())
    
    if st.button("Show the best series"):
        top_series = get_top_series_by_genre_and_subgenre(genre, subgenres)
        for series in top_series:
            st.write(f"**✨{series['Title']}✨**")
            st.write(f"🎭 Genre: {series['Genre']}")
            st.write(f"🎥 Cast: {series['Cast']}")
            st.write(f"⭐️ Rating: {series['Rating']}")
            st.write(f"**🎬 Synopsis:** {series['Synopsis']}")
            st.markdown("---")  # Línea horizontal separadora

elif page == "Our Story":
    ## st.write(get_company_history())
     # Título
    st.markdown("### Bienvenido a nuestra plataforma de recomendación de series, un proyecto de la **Fundación HC Bank**.")
    
    # Explicación sobre la Fundación HC Bank
    st.markdown("""
    La **Fundación HC Bank** es una iniciativa del **HC Bank** que busca fomentar el acceso a la cultura y el entretenimiento para personas de todas las edades. 
    Nació con el propósito de difundir la cultura y conectar generaciones a través de diversas formas de expresión artística, 
    utilizando la tecnología para llevar el contenido cultural de una manera innovadora y accesible.
    """)
    
    # Mostrar el logo
    st.image("resources/logo_hcbank.jpeg", width=200)

    # Resto del texto
    st.markdown("""
    Este proyecto nace en 2024 como parte de nuestro compromiso con la difusión cultural, utilizando la tecnología más avanzada para ofrecer una experiencia única. 
    A través de nuestra plataforma, queremos facilitar el descubrimiento de contenido audiovisual de calidad, adaptado a los gustos y emociones de cada usuario.

    Con la ayuda de la inteligencia artificial y herramientas de recomendación, nuestra app te sugiere contenido basado en tus preferencias, para que disfrutes de nuevas joyas y expandas tus horizontes culturales. 
    
    ¡Gracias por unirte a nosotros en este viaje cultural! Esperamos que encuentres tu próxima serie favorita.
    """)

elif page == "Moods":
    st.markdown("""
        ### Moods
        Feeling a certain way? 
        Choose a mood that matches your current vibe and we'll recommend the best series for you! 
        Whether you want something funny, romantic, or adventurous, we've got you covered.
        """)
    # Pregunta al usuario qué estado de ánimo le apetece ver
    selected_mood = st.selectbox("What do you feel like watching today?", ['😂 Fun 😂', '🥰 Romantic 🥰', '😢 Sad 😢', '🤠 Adventurous 🤠', '🫣 Tense 🫣', '🤪 Mixed 🤪'])

    if st.button("Buscar"):
        # Filtrar las series según el estado de ánimo seleccionado
        recommended_series = df[df['Mood'] == selected_mood]
        
        if not recommended_series.empty:
            # Obtener las 10 mejores series según el rating
            recommended_series = recommended_series[recommended_series['Number of Votes'] >= 10000]
            top_series = recommended_series.nlargest(10, 'Rating')
            
            if not top_series.empty:
                for _, series in top_series.iterrows():
                    st.write(f"**✨{series['Title']}✨**")
                    st.write(f"🎭 Genre: {series['Main Genre']}")
                    st.write(f"🎥 Cast: {series['Cast']}")
                    st.write(f"⭐️ Rating: {series['Rating']}")
                    st.write(f"**🎬 Synopsis:** {series['Synopsis']}")
                    st.markdown("---")
            else:
                st.warning("No highly-rated shows were found for this mood.")
        else:
            st.warning("No shows were found for this mood.")
