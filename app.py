import streamlit as st
import pandas as pd
from sentence_transformers import SentenceTransformer
from pinecone import Pinecone


# Cargar el DataFrame
df = pd.read_csv("data/clean_data/series.csv")  # Reemplaza con la ruta a tu archivo CSV

# Inicializa el modelo de embeddings
model = SentenceTransformer('all-MiniLM-L6-v2')  # O el modelo que hayas elegido

# Conecta a Pinecone
pc = Pinecone(api_key="2c3b8e05-b4f8-4c38-82f1-6e41ac7fbcd1")  # Reemplaza con tu clave de API
index = pc.Index('series')  # Asegúrate de que el índice 'series' exista



# Función de búsqueda
def search_series(query, search_type, min_rating):
    if search_type == 'Synopsis':
        # Genera un vector para la consulta
        vector = model.encode(query).tolist()
        # Realiza la búsqueda en Pinecone usando argumentos nombrados
        results = index.query(vector=vector, top_k=5, include_values=True)
        # Obtiene los IDs y valores de los resultados
        recommended_series = []
        for match in results['matches']:
            series_id = match['id']
            score = match['score']
            # Busca en el DataFrame original para obtener más información sobre la serie
            series_info = df[df['IMDb ID'] == series_id].iloc[0]  # Asegúrate de que el índice sea correcto
            # Filtrar series con al menos 20000 valoraciones
            if series_info['Number of Votes'] >= 10000 and series_info['Rating'] >= min_rating:
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
    
    if subgenres:  # Solo si hay subgéneros seleccionados
        filtered_series = filtered_series[filtered_series['Genre'].str.contains('|'.join(subgenres), case=False)]
    filtered_series = filtered_series[filtered_series['Number of Votes'] >= 10000]
    top_series = filtered_series.nlargest(n, 'Rating')
    return top_series.to_dict('records')

# Función para obtener la historia de la empresa
def get_company_history():
    return """
    Bienvenido a nuestra plataforma de recomendación de series. 
    Nuestra misión es ayudar a los amantes de las series a encontrar nuevas joyas y disfrutar de contenido de calidad. 
    Fundada en 2023, nuestra empresa se basa en la tecnología de IA para ofrecerte las mejores recomendaciones personalizadas.
    """

# Interfaz de usuario en Streamlit
st.title("🛋️🎉 Aventuras en el Sofá: ¡Maratones Épicos! 🍿🎬")
# Agregar una imagen en la barra lateral
st.sidebar.image("resources/princess_photo.jpeg", caption="🎬Your next adventure in entertainment starts here!🍿", use_column_width=True)
# Navegación de páginas
page = st.sidebar.radio("Select a page", ["Our Story", "Top 10 Series", "Moods", "Recommender"])


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
                # Muestra los resultados con imagen al lado
                for series in results:
                    st.write(f"**✨{series['Title']}✨**")
                    st.write(f"🎭 Genre: {series['Genre']}")
                    st.write(f"🎥 Cast: {series['Cast']}")
                    st.write(f"⭐️ Rating: {series['Rating']}")
                    st.write(f"**🎬 Synopsis:** {series['Synopsis']}")
                    st.markdown("---")
            else:
                results = search_series(query, search_type, rating_filter)
                # Muestra los resultados con imagen al lado
                for series in results:
                    st.write(f"**✨{series['Title']}✨**")  # Título de la serie
                    st.write(f"🎭 Genre: {series['Genre']}")  # Género de la serie
                    st.write(f"🎥 Cast: {series['Cast']}")  # Reparto de la serie
                    st.write(f"⭐️ Rating: {series['Rating']}: estrella:")
                    st.write(f"**🎬 Synopsis:** {series['Synopsis']}")  # Sinopsis de la serie
                    st.markdown("---")
        else:
            st.warning("Please enter a search term.")
elif page == "Top 10 Series":
    st.markdown("""
    ### Top 10 Series
    Discover the best series according to your preferences! 
    You can select a main genre and even choose subgenres to narrow down your options. 
    Our top-rated recommendations will help you find the most acclaimed shows to watch.
    """)
    # Seleccionar un género principal
    genre = st.selectbox("Seleccione un género", df['Main Genre'].unique())
    # Seleccionar subgéneros (puede seleccionar múltiples)
    subgenres = st.multiselect("¿Quieres elegir un subgénero?", df['Genre'].str.split(',').explode().unique())
    
    if st.button("Mostrar las mejores series"):
        top_series = get_top_series_by_genre_and_subgenre(genre, subgenres)
        for series in top_series:
            st.write(f"**✨{series['Title']}✨**")
            st.write(f"🎭 Genre: {series['Genre']}")
            st.write(f"🎥 Cast: {series['Cast']}")
            st.write(f"⭐️ Rating: {series['Rating']}")
            st.write(f"**🎬 Synopsis:** {series['Synopsis']}")
            st.markdown("---")  # Línea horizontal separadora

elif page == "Our Story":
    st.write(get_company_history())

elif page == "Moods":
    st.markdown("""
        ### Moods
        Feeling a certain way? 
        Choose a mood that matches your current vibe and we'll recommend the best series for you! 
        Whether you want something funny, romantic, or adventurous, we've got you covered.
        """)
    # Pregunta al usuario qué estado de ánimo le apetece ver
    selected_mood = st.selectbox("¿Qué te apetece ver hoy?", ['😂 Divertido 😂', '🥰 Romántico 🥰', '😢 Triste 😢', '🤠 Aventurero 🤠', '🥹 Inspirador 🥹', '🫣 Tenso 🫣', '🤪 Variado 🤪'])

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
                    st.write(f"🎭 Género: {series['Main Genre']}")
                    st.write(f"🎥 Reparto: {series['Cast']}")
                    st.write(f"⭐️ Calificación: {series['Rating']}")
                    st.write(f"**🎬 Sinopsis:** {series['Synopsis']}")
                    st.markdown("---")
            else:
                st.warning("No se encontraron series con calificación alta para este estado de ánimo.")
        else:
            st.warning("No se encontraron series para este estado de ánimo.")
