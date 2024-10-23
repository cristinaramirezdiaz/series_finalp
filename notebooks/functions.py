import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from wordcloud import WordCloud
from matplotlib.colors import LinearSegmentedColormap

def load_data():
    """
    Load data from all genre CSV files and concatenate them into a single DataFrame
    """
    # Load each genre CSV file
    action = pd.read_csv('../data/action_series.csv')
    adventure = pd.read_csv('../data/adventure_series.csv')
    animation = pd.read_csv('../data/animation_series.csv')
    biography = pd.read_csv('../data/biography_series.csv')
    comedy = pd.read_csv('../data/comedy_series.csv')
    crime = pd.read_csv('../data/crime_series.csv')
    documentary = pd.read_csv('../data/documentary_series.csv')
    drama = pd.read_csv('../data/drama_series.csv')
    family = pd.read_csv('../data/family_series.csv')
    fantasy = pd.read_csv('../data/fantasy_series.csv')
    history = pd.read_csv('../data/history_series.csv')
    horror = pd.read_csv('../data/horror_series.csv')
    music = pd.read_csv('../data/music_series.csv')
    musical = pd.read_csv('../data/musical_series.csv')
    mystery = pd.read_csv('../data/mystery_series.csv')
    romance = pd.read_csv('../data/romance_series.csv')
    sci_fi = pd.read_csv('../data/sci-fi_series.csv')
    sport = pd.read_csv('../data/sport_series.csv')
    superhero = pd.read_csv('../data/superhero_series.csv')
    thriller = pd.read_csv('../data/thriller_series.csv')
    war = pd.read_csv('../data/war_series.csv')
    western = pd.read_csv('../data/western_series.csv')

    # Concatenate all DataFrames into one
    df = pd.concat([action, adventure, animation, biography, 
                    comedy, crime, documentary, drama, family, fantasy, history, horror, music, 
                    musical, mystery, romance, sci_fi, sport, superhero, thriller, war, western], axis=0)

    return df


def drop_columns(df):
    """
    Drop columns that are not useful for the analysis from the DataFrame

    Parameters
    ----------
    df : pandas.DataFrame
        The DataFrame to drop columns from

    Returns
    -------
    pandas.DataFrame
        The DataFrame with the columns dropped
    """
    # Drop columns that are not useful for the analysis
    df = df.drop(columns=['Runtime', 'Certificate', 'Gross Revenue'])
    return df

def clean_data(df):
    """
    Clean the DataFrame by removing NaN values, duplicates, and non-numeric
    values in the 'Number of Votes' column

    Parameters
    ----------
    df : pandas.DataFrame
        The DataFrame to clean

    Returns
    -------
    pandas.DataFrame
        The cleaned DataFrame
    """
    # Drop rows with NaN values
    df = df.dropna()

    # Drop duplicate rows
    df = df.drop_duplicates()

    # Drop rows with non-numeric values in the 'Number of Votes' column
    df['Number of Votes'] = pd.to_numeric(df['Number of Votes'], errors='coerce')
    df = df.dropna(subset=['Number of Votes'])

    return df

def unique_films(df):
    """
    Return a DataFrame with unique films ordered by the number of votes in a descending order.

    The DataFrame is sorted by the 'Number of Votes' column in a descending order. The
    `drop_duplicates` method is used with the `subset` parameter set to `['Title', 'IMDb ID']`
    to drop duplicate rows, keeping the first occurrence of each unique film.

    Parameters
    ----------
    df : pandas.DataFrame
        The DataFrame to process

    Returns
    -------
    pandas.DataFrame
        The DataFrame with unique films
    """
    df = df.sort_values('Number of Votes', ascending=False).drop_duplicates(
        subset=['Title', 'IMDb ID'],
        keep='first')
    return df


def new_columns(df):
    """
    Add new columns to the DataFrame

    This function adds two new columns to the DataFrame:
    - `embedding`: a column that concatenates the `Title` and `Synopsis` columns
    - `Main Genre`: a column that extracts the first genre from the `Genre` column

    Parameters
    ----------
    df : pandas.DataFrame
        The DataFrame to process

    Returns
    -------
    pandas.DataFrame
        The DataFrame with the new columns
    """
    # Add a new column that concatenates the Title and Synopsis columns
    df['embedding'] = df['Title'] + ' ' + df['Synopsis']

    # Add a new column that extracts the first genre from the Genre column
    df['Main Genre'] = df['Genre'].str.split(',').str[0]

    return df

def classify_mood(genre):
    """
    Classify a genre into a mood category

    This function takes a genre as input and returns a mood category based on the genre.
    The categories are:
    - '😂 Fun 😂': comedy, animation, family, fantasy, musical, music, reality-tv
    - '🥰 Romantic 🥰': romance
    - '😢 Sad 😢': drama, documentary, biography
    - '🤠 Adventurous 🤠': adventure, sci-fi, action, war, western
    - '🫣 Tense 🫣': thriller, crime, mystery, horror
    - '🤪 Mixed 🤪': any other genre

    Parameters
    ----------
    genre : str
        The genre to classify

    Returns
    -------
    str
        The mood category
    """
    genre = genre.lower()  # Convert to lowercase for comparison
    if any(g in genre for g in ['comedy', 'animation', 'family', 'fantasy', 'musical', 'music', 'reality-tv']):
        # Genres that are generally considered fun
        return '😂 Fun 😂'
    elif any(g in genre for g in ['romance']):
        # Genres that are generally considered romantic
        return '🥰 Romantic 🥰'
    elif any(g in genre for g in ['drama', 'documentary', 'biography']):
        # Genres that are generally considered sad
        return '😢 Sad 😢'
    elif any(g in genre for g in ['adventure', 'sci-fi', 'action', 'war', 'western']):
        # Genres that are generally considered adventurous
        return '🤠 Adventurous 🤠'
    elif any(g in genre for g in ['thriller', 'crime', 'mystery', 'horror']):
        # Genres that are generally considered tense
        return '🫣 Tense 🫣'
    else:
        # Any other genre is considered mixed
        return '🤪 Mixed 🤪'

def to_csv(df):
    """
    Save the cleaned DataFrame to a CSV file

    Parameters
    ----------
    df : pandas.DataFrame
        The DataFrame to save

    Returns
    -------
    pandas.DataFrame
        The same DataFrame
    """
    # Save the DataFrame to a CSV file
    df.to_csv('../data/clean_data/series.csv', index=False)
    return df

def generate_word_cloud(df):
    """
    Generate a word cloud of the main genres in the DataFrame.

    Parameters
    ----------
    df : pandas.DataFrame
        The DataFrame containing the 'Main Genre' column

    Returns
    -------
    None
    """
    # Define the colors for the word cloud
    colors = ["#a564d3", "#d689ff", "#431259", "#9b72cf", "#5a108f"]
 
    # Create a custom color map for the word cloud
    custom_cmap = LinearSegmentedColormap.from_list("violet", colors)

    # Get the frequency of each main genre
    genre_frequencies = df['Main Genre'].value_counts()

    # Generate the word cloud
    wordcloud = WordCloud(width=800, height=400, background_color="white", colormap=custom_cmap).generate_from_frequencies(genre_frequencies)

    # Plot the word cloud
    plt.figure(figsize=(10, 5))
    plt.imshow(wordcloud, interpolation="bilinear")
    plt.axis("off")
    plt.title("Word Cloud of Main Genres")
    plt.show()

def plot_main_genre_distribution(df):
    """
    Plot the distribution of main genres in the DataFrame.

    This function takes a DataFrame as input and plots a bar chart of the main genres
    and their corresponding counts.

    Parameters
    ----------
    df : pandas.DataFrame
        The DataFrame containing the 'Main Genre' column

    Returns
    -------
    None
    """
    # Set the seaborn style to whitegrid
    sns.set(style="whitegrid")

    # Create a new figure with a specified size
    plt.figure(figsize=(10, 6))

    # Get the counts of each main genre
    main_genre_counts = df['Main Genre'].value_counts()

    # Plot the bar chart
    sns.barplot(x=main_genre_counts.values, y=main_genre_counts.index, palette="viridis")
    plt.title('Distribution of Main Genre')
    plt.xlabel('Number of Shows')
    plt.ylabel('Main Genre')
    plt.show()


def plot_ratings_distribution(df):
    """
    Plot the distribution of ratings in the DataFrame.

    This function takes a DataFrame as input and plots a histogram of the ratings
    with a kernel density estimate (KDE) of the distribution.

    Parameters
    ----------
    df : pandas.DataFrame
        The DataFrame containing the 'Rating' column

    Returns
    -------
    None
    """
    # Set the seaborn style to whitegrid
    sns.set(style="whitegrid")

    # Create a new figure with a specified size
    plt.figure(figsize=(10, 6))

    # Plot the histogram and KDE of the ratings
    sns.histplot(df['Rating'], bins=20, kde=True, color='blue')

    # Set the title and labels
    plt.title('Distribution of Ratings')
    plt.xlabel('Rating')
    plt.ylabel('Count')

    # Show the plot
    plt.show()



def plot_ratings_vs_votes(df):
    """
    Plot the relationship between ratings and the number of votes for each show.

    This function takes a DataFrame as input and plots a scatter plot of the ratings
    against the number of votes. The size of the points is determined by the number of
    votes, and the color is determined by the main genre.

    Parameters
    ----------
    df : pandas.DataFrame
        The DataFrame containing the 'Rating', 'Number of Votes', and 'Main Genre' columns

    Returns
    -------
    None
    """
    # Set the seaborn style to whitegrid
    sns.set(style="whitegrid")

    # Create a new figure with a specified size
    plt.figure(figsize=(10, 6))

    # Plot the scatter plot
    sns.scatterplot(data=df, x='Rating', y='Number of Votes', 
                    hue='Main Genre', size='Number of Votes', 
                    sizes=(20, 200), palette='viridis', alpha=0.7, edgecolor='w')
    # Set the title and labels
    plt.title('Ratings vs Number of Votes')
    plt.xlabel('Rating')
    plt.ylabel('Number of Votes')
    # Put the legend on the right side
    plt.legend(loc='upper left', bbox_to_anchor=(1, 1))

    # Show the plot
    plt.show()


def plot_average_ratings_by_genre(df):
    """
    Plot the average ratings for each main genre in a horizontal bar chart.

    Parameters
    ----------
    df : pandas.DataFrame
        The DataFrame containing the 'Rating' and 'Main Genre' columns

    Returns
    -------
    None
    """
    plt.style.use('ggplot')

    # Group the DataFrame by 'Main Genre', calculate the average rating for each group,
    # and sort the results by average rating
    average_ratings = df.groupby('Main Genre')['Rating'].mean().sort_values()

    # Create a new figure with a specified size
    plt.figure(figsize=(12, 6))

    # Plot the horizontal bar chart
    average_ratings.plot(kind='barh', color='skyblue')

    # Set the title and labels
    plt.title('Average Ratings by Main Genre')
    plt.xlabel('Average Rating')
    plt.ylabel('Main Genre')

    # Set the x-axis limits to 0-10
    plt.xlim(0, 10)

    # Show the plot
    plt.show()


def plot_top_10_votes(df):
    """
    Plot the top 10 movies or series with the most votes.

    This function ensures that the 'Number of Votes' column is in numeric format, sorts the DataFrame by 
    'Number of Votes' in descending order, selects the top 10 entries, and creates a bar plot to visualize 
    the data.

    Parameters
    ----------
    df : pandas.DataFrame
        The DataFrame containing the 'Number of Votes' and 'Title' columns

    Returns
    -------
    None
    """
    # Ensure that the 'Number of Votes' column is in numeric format
    df['Number of Votes'] = pd.to_numeric(df['Number of Votes'], errors='coerce')

    # Sort the DataFrame by 'Number of Votes' in descending order and select the top 10 entries
    top_10_votes = df.nlargest(10, 'Number of Votes')

    # Create the bar plot
    plt.figure(figsize=(12, 6))
    sns.barplot(x='Number of Votes', y='Title', data=top_10_votes, palette='viridis')
    plt.title('Top 10 Movies/Series with Most Votes')
    plt.xlabel('Number of Votes')
    plt.ylabel('Title')
    plt.show()
