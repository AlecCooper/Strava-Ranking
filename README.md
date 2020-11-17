# Strava-Ranking

Strava is a popular fitness tracking social media platform that allows friends to remotely race against one another using gps data. Recently, many popular user ranking features were put behind a paywall reserved only for premium users. This simple django based web app allows for custom rankings to be created between friends. It utilizes the Strava REST API to pull user data and create rankings based upon custom chosen segments. It comes fully containerized, utilizing Docker, nginx, Gunicorn and PostgreSQL.
