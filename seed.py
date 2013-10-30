import model
import csv
import datetime

def load_users(session):
    # use u.user
    with open("seed_data/u.user", "rb") as csvfile:
        users = csv.reader(csvfile, delimiter= '|')
        for user in users:
            new_user = model.User(id=user[0], age=user[1], zipcode=user[4])
            session.add(new_user)
    session.commit()

def load_movies(session):
    # use u.item
    with open("seed_data/u.item", "rb") as csvfile:
        movies = csv.reader(csvfile, delimiter= '|')
        for movie in movies:
            try:
                date = str(datetime.datetime.strptime(movie[2], '%d-%b-%Y'))
                split_date = date.split()[0].split("-")
                release_date = datetime.date(int(split_date[0]), int(split_date[1]), int(split_date[2]))
                new_movie = model.Movie(id=movie[0], name=movie[1].decode("latin-1"), released_at=release_date, imdb_url=movie[4])
                session.add(new_movie)
            except:
                continue
    session.commit()

def load_ratings(session):
    # use u.data
    with open("seed_data/u.data", "rb") as csvfile:
        ratings = csv.reader(csvfile, delimiter="\t")
        for rating in ratings:
            date = str(datetime.datetime.fromtimestamp(float(rating[3]))).split()[0]
            new_rating = model.Rating(user_id=rating[0], movie_id=rating[1], rating=rating[2], timestamp=date)
            session.add(new_rating)
    session.commit()

def main(session):
    # You'll call each of the load_* functions with the session as an argument
    load_users(s)
    load_movies(s)
    load_ratings(s)

if __name__ == "__main__":
    s = model.connect()
    main(s)