import { useEffect, useState } from "react";
import "./App.css";

const API_URL = "http://57.181.174.40:5000";

function App() {
  // Login / Register
  const [isLogin, setIsLogin] = useState(true);

  const [name, setName] = useState("");
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");

  // User and messages
  const [user, setUser] = useState(null);
  const [message, setMessage] = useState("");

  // Movies
  const [movies, setMovies] = useState([]);
  const [selectedMovie, setSelectedMovie] = useState(null);

  // User data
  const [favorites, setFavorites] = useState([]);
  const [watchHistory, setWatchHistory] = useState([]);

  // --------------------------------------------------
  // FETCH MOVIES AFTER LOGIN
  // --------------------------------------------------

  useEffect(() => {
    if (user) {
      fetch(API_URL + "/movies")
        .then((response) => response.json())
        .then((data) => {
          setMovies(data);
        })
        .catch((error) => {
          console.error("Error fetching movies:", error);
        });
    }
  }, [user]);

  // --------------------------------------------------
  // FETCH FAVORITES AFTER LOGIN
  // --------------------------------------------------

  useEffect(() => {
    if (user) {
      fetch(API_URL + `/favorites/${user.user_id}`)
        .then((response) => response.json())
        .then((data) => {
          setFavorites(data);
        })
        .catch((error) => {
          console.error("Error fetching favorites:", error);
        });
    }
  }, [user]);

  // --------------------------------------------------
  // FETCH WATCH HISTORY AFTER LOGIN
  // --------------------------------------------------

  useEffect(() => {
    if (user) {
      fetch(API_URL + `/watch-history/${user.user_id}`)
        .then((response) => response.json())
        .then((data) => {
          setWatchHistory(data);
        })
        .catch((error) => {
          console.error("Error fetching watch history:", error);
        });
    }
  }, [user]);

  // --------------------------------------------------
  // LOGIN / REGISTER
  // --------------------------------------------------

  const handleSubmit = async (e) => {
    e.preventDefault();

    const endpoint = isLogin ? "/login" : "/register";

    const body = isLogin
      ? {
          email: email,
          password: password,
        }
      : {
          name: name,
          email: email,
          password: password,
        };

    try {
      const response = await fetch(API_URL + endpoint, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify(body),
      });

      const data = await response.json();

      if (response.ok) {
        setMessage(data.message);

        if (isLogin) {
          setUser(data);
        }
      } else {
        setMessage(data.message || "Something went wrong");
      }
    } catch (error) {
      console.error(error);
      setMessage("Unable to connect to backend");
    }
  };

  // --------------------------------------------------
  // OPEN MOVIE DETAILS
  // --------------------------------------------------

  const openMovie = async (movie) => {
    setSelectedMovie(movie);
    setMessage("");

    // Add movie to watch history
    try {
      const response = await fetch(API_URL + "/watch-history", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          user_id: user.user_id,
          movie_id: movie.id,
        }),
      });

      if (response.ok) {
        // Refresh watch history
        const historyResponse = await fetch(
          API_URL + `/watch-history/${user.user_id}`
        );

        const historyData = await historyResponse.json();

        setWatchHistory(historyData);
      }
    } catch (error) {
      console.error("Error adding watch history:", error);
    }
  };

  // --------------------------------------------------
  // ADD FAVORITE
  // --------------------------------------------------

  const addFavorite = async (movieId) => {
    try {
      const response = await fetch(API_URL + "/favorites", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          user_id: user.user_id,
          movie_id: movieId,
        }),
      });

      const data = await response.json();

      if (response.ok) {
        const movie = movies.find(
          (item) => item.id === movieId
        );

        setFavorites([...favorites, movie]);

        setMessage("❤️ Movie added to favorites");
      } else {
        setMessage(data.message || "Unable to add favorite");
      }
    } catch (error) {
      console.error(error);
      setMessage("Unable to connect to backend");
    }
  };

  // --------------------------------------------------
  // REMOVE FAVORITE
  // --------------------------------------------------

  const removeFavorite = async (movieId) => {
    try {
      const response = await fetch(
        API_URL + `/favorites/${user.user_id}/${movieId}`,
        {
          method: "DELETE",
        }
      );

      const data = await response.json();

      if (response.ok) {
        setFavorites(
          favorites.filter(
            (movie) => movie.id !== movieId
          )
        );

        setMessage("Movie removed from favorites");
      } else {
        setMessage(
          data.message || "Unable to remove favorite"
        );
      }
    } catch (error) {
      console.error(error);
      setMessage("Unable to connect to backend");
    }
  };

  // --------------------------------------------------
  // CHECK FAVORITE
  // --------------------------------------------------

  const isFavorite = (movieId) => {
    return favorites.some(
      (movie) => movie.id === movieId
    );
  };

  // --------------------------------------------------
  // LOGOUT
  // --------------------------------------------------

  const logout = () => {
    setUser(null);
    setSelectedMovie(null);
    setFavorites([]);
    setWatchHistory([]);
    setMessage("");
    setName("");
    setEmail("");
    setPassword("");
  };

  // ==================================================
  // LOGINED USER
  // ==================================================

  if (user) {

    // ------------------------------------------------
    // MOVIE DETAILS PAGE
    // ------------------------------------------------

    if (selectedMovie) {
      return (
        <div className="app">

          <nav className="navbar">

            <div className="logo">
              NETFLIX CLONE
            </div>

            <button
              className="logout"
              onClick={logout}
            >
              Logout
            </button>

          </nav>

          <section className="hero">

            <button
              onClick={() => setSelectedMovie(null)}
            >
              ← Back to Movies
            </button>

            <h1>{selectedMovie.title}</h1>

            <p>
              {selectedMovie.description}
            </p>

            <p>
              Genre: {selectedMovie.genre}
            </p>

            <p>
              Release Year: {selectedMovie.release_year}
            </p>

            <p className="rating">
              ⭐ {selectedMovie.rating}
            </p>

            <br />

            {isFavorite(selectedMovie.id) ? (

              <button
                onClick={() =>
                  removeFavorite(selectedMovie.id)
                }
              >
                💔 Remove from Favorites
              </button>

            ) : (

              <button
                onClick={() =>
                  addFavorite(selectedMovie.id)
                }
              >
                ❤️ Add to Favorites
              </button>

            )}

            <p>{message}</p>

          </section>

        </div>
      );
    }

    // ------------------------------------------------
    // MOVIE HOMEPAGE
    // ------------------------------------------------

    return (
      <div className="app">

        {/* NAVBAR */}

        <nav className="navbar">

          <div className="logo">
            NETFLIX CLONE
          </div>

          <button
            className="logout"
            onClick={logout}
          >
            Logout
          </button>

        </nav>


        {/* HERO */}

        <section className="hero">

          <h1>
            Welcome, {user.name}!
          </h1>

          <p>
            Watch your favorite movies and discover
            something new.
          </p>

        </section>


        {/* MESSAGE */}

        {message && (
          <div className="movies-section">
            <p>{message}</p>
          </div>
        )}


        {/* MOVIES */}

        <section className="movies-section">

          <h2>Movies 🎬</h2>

          <div className="movies-grid">

            {movies.map((movie) => (

              <div
                className="movie-card"
                key={movie.id}
                onClick={() => openMovie(movie)}
              >

                <h3>
                  {movie.title}
                </h3>

                <p className="movie-description">
                  {movie.description}
                </p>

                <p className="movie-info">
                  {movie.genre} • {movie.release_year}
                </p>

                <p className="rating">
                  ⭐ {movie.rating}
                </p>

              </div>

            ))}

          </div>

        </section>


        {/* FAVORITES */}

        <section className="movies-section">

          <h2>
            ❤️ My Favorites
          </h2>

          {favorites.length === 0 ? (

            <p>
              No favorite movies yet.
            </p>

          ) : (

            <div className="movies-grid">

              {favorites.map((movie) => (

                <div
                  className="movie-card"
                  key={movie.id}
                  onClick={() => openMovie(movie)}
                >

                  <h3>
                    {movie.title}
                  </h3>

                  <p className="movie-description">
                    {movie.description}
                  </p>

                  <p className="movie-info">
                    {movie.genre} • {movie.release_year}
                  </p>

                  <p className="rating">
                    ⭐ {movie.rating}
                  </p>

                  <button
                    onClick={(e) => {
                      e.stopPropagation();
                      removeFavorite(movie.id);
                    }}
                  >
                    💔 Remove
                  </button>

                </div>

              ))}

            </div>

          )}

        </section>


        {/* WATCH HISTORY */}

        <section className="movies-section">

          <h2>
            🕐 Watch History
          </h2>

          {watchHistory.length === 0 ? (

            <p>
              No watch history yet.
            </p>

          ) : (

            <div className="movies-grid">

              {watchHistory.map((movie) => (

                <div
                  className="movie-card"
                  key={movie.id + movie.watched_at}
                  onClick={() => openMovie(movie)}
                >

                  <h3>
                    {movie.title}
                  </h3>

                  <p className="movie-info">
                    {movie.genre} • {movie.release_year}
                  </p>

                  <p className="rating">
                    ⭐ {movie.rating}
                  </p>

                  <p className="movie-info">
                    Watched: {movie.watched_at}
                  </p>

                </div>

              ))}

            </div>

          )}

        </section>

      </div>
    );
  }

  // ==================================================
  // ==================================================
  // LOGIN / REGISTER PAGE
  // ==================================================

  return (
    <div className="login-page">

      <div className="login-box">

        <div className="login-logo">
          NETFLIX CLONE
        </div>

        <h2>
          {isLogin ? "Sign In" : "Create Account"}
        </h2>

        <form onSubmit={handleSubmit}>

          {!isLogin && (
            <div>
              <label>Name</label>

              <input
                type="text"
                value={name}
                onChange={(e) => setName(e.target.value)}
                placeholder="Enter your name"
                required
              />
            </div>
          )}

          <div>
            <label>Email</label>

            <input
              type="email"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              placeholder="Enter your email"
              required
            />
          </div>

          <div>
            <label>Password</label>

            <input
              type="password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              placeholder="Enter your password"
              required
            />
          </div>

          <button
            type="submit"
            className="login-button"
          >
            {isLogin ? "Sign In" : "Register"}
          </button>

        </form>

        {message && (
          <p className="message">
            {message}
          </p>
        )}

        <button
          className="switch-button"
          onClick={() => {
            setIsLogin(!isLogin);
            setMessage("");
            setName("");
            setEmail("");
            setPassword("");
          }}
        >
          {isLogin
            ? "New to Netflix Clone? Create an account"
            : "Already have an account? Sign in"}
        </button>

      </div>

    </div>
  );
}

export default App;

