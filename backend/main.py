from fastapi import FastAPI
from backend.REST_API.dtt_class import *
from query_processor import QueryProcessor

# tmux attach -t fastapi
# ctrl + B, D  세션 나오기
# ctrl + C  fastapi 종료
# uvicorn main:app --host 0.0.0.0 --port 8000 --reload  다시 실행

app = FastAPI()

dummy_movies = [
    ReturnMovie(title="Inception", genre="Sci-Fi", age_rating="PG-13", country="USA", release_date="2010-07-16", running_time=148, description="A thief who steals corporate secrets through the use of dream-sharing technology is given the inverse task of planting an idea into the mind of a CEO."),
    ReturnMovie(title="The Dark Knight", genre="Action", age_rating="PG-13", country="USA", release_date="2008-07-18", running_time=152, description="When the menace known as The Joker emerges from his mysterious past, he wreaks havoc and chaos on the people of Gotham."),
    ReturnMovie(title="Titanic", genre="Drama", age_rating="PG-13", country="USA", release_date="1997-12-19", running_time=195, description="A seventeen-year-old aristocrat falls in love with a kind but poor artist aboard the luxurious, ill-fated R.M.S. Titanic."),
    ReturnMovie(title="The Godfather", genre="Crime", age_rating="R", country="USA", release_date="1972-03-24", running_time=175, description="The aging patriarch of an organized crime dynasty transfers control of his clandestine empire to his reluctant son."),
    ReturnMovie(title="The Shawshank Redemption", genre="Drama", age_rating="R", country="USA", release_date="1994-09-22", running_time=142, description="Two imprisoned men bond over a number of years, finding solace and eventual redemption through acts of common decency."),
    ReturnMovie(title="The Avengers", genre="Action", age_rating="PG-13", country="USA", release_date="2012-05-04", running_time=143, description="Earth's mightiest heroes must come together and learn to fight as a team if they are going to stop the mischievous Loki and his alien army from subjugating Earth."),
    ReturnMovie(title="Jurassic Park", genre="Adventure", age_rating="PG-13", country="USA", release_date="1993-06-11", running_time=127, description="During a preview tour, a theme park suffers a major power breakdown that allows its cloned dinosaur exhibits to run amok."),
    ReturnMovie(title="Pulp Fiction", genre="Crime", age_rating="R", country="USA", release_date="1994-10-14", running_time=154, description="The lives of two mob hitmen, a boxer, a gangster's wife, and a pair of diner bandits intertwine in four tales of violence and redemption."),
    ReturnMovie(title="Forrest Gump", genre="Drama", age_rating="PG-13", country="USA", release_date="1994-07-06", running_time=142, description="The presidencies of Kennedy and Johnson, the Vietnam War, the Nixon years, the Watergate scandal and other historical events unfold from the perspective of an Alabama man with an extraordinary quality."),
    ReturnMovie(title="The Matrix", genre="Sci-Fi", age_rating="R", country="USA", release_date="1999-03-31", running_time=136, description="A computer hacker learns from mysterious rebels about the true nature of his reality and his role in the war against its controllers.")
]

@app.get("/")
async def read_root():
    return {"watch-me root directory"}

@app.post("/main_page/")
async def main_page_query(item: MainPage):
    query_processor = QueryProcessor()
    return {"movies": dummy_movies[:10]}

@app.get("/search_page/")
async def search_page_query(item: SearchPage):
    query_processor = QueryProcessor()
    return query_processor.process_search_page(item)
