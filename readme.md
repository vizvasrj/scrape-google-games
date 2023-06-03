use this command to start it

``docker-compose up --build``


to start worker to fetch games data from https://play.google.com/store/games?hl=en&gl=US

```bash
curl localhost:5000/api/apps
```


to get specific game data by id use 

```bash
curl localhost:5000/get_details?app_id=com.kiloo.subwaysurf
```

as `com.kiloo.subwaysurf` is app id
