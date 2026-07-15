import csv, requests, io
from fastapi import FastAPI, Request
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles

import uvicorn

app = FastAPI()
templates = Jinja2Templates(directory="templates")

# Μετά το app = FastAPI()
app.mount("/static", StaticFiles(directory="static"), name="static")

def get_matches():
    # Αυτό είναι το σωστό link από το google sheet
    CSV_URL = "https://docs.google.com/spreadsheets/d/e/2PACX-1vSFQQ3cyNYfBbQoizYYMUbays86Y-Gji1vPIux28Ds8DbrNZLpQY7BzpEySPHb27ofbMdaq4O15oFDU/pub?output=csv"
    try:
        # Εδώ άλλαξα το 'url' σε 'CSV_URL'
        response = requests.get(CSV_URL)
        response.raise_for_status() # Αυτό θα μας πει αν το link έχει θέμα
        content = response.content.decode('utf-8-sig')
        return list(csv.DictReader(io.StringIO(content)))
    except Exception as e:
        print(f"Σφάλμα στο κατέβασμα: {e}") # Τώρα θα δούμε τι φταίει αν αποτύχει
        return []

@app.get("/", response_class=HTMLResponse)
def read_root(request: Request):
    all_matches = get_matches()
    upcoming = []
    
    for m in all_matches:
        if m.get('status') == 'open':
            country = m.get('country', '')
            team_name = "ΑΡΗΣ" if country == 'gr' else "ARIS"
            
            home = m.get('home_team', '')
            away = m.get('away_team', '')
            
            if home == "ARIS" or home == "ΑΡΗΣ":
                opponent = away
                is_home = True
            else:
                opponent = home
                is_home = False
            
            match_obj = {
                "date": m.get('date_time'),
                "competition": m.get('tournament'),
                "sport": m.get('sport'),
                "team_name": team_name,
                "opponent": opponent,
                "is_home": is_home
            }
            upcoming.append(match_obj)
    upcoming = upcoming[:5]
            
    return templates.TemplateResponse(request=request, name="index.html", context={"upcoming": upcoming})

@app.get("/sport/{sport_name}", response_class=HTMLResponse)
@app.get("/sport/{sport_name}", response_class=HTMLResponse)
def read_sport(request: Request, sport_name: str):
    all_matches = get_matches()
    sport_data = [m for m in all_matches if sport_name.lower() in m.get('sport', '').lower()]
    upcoming = []
    completed = []
    
    for m in sport_data:
        # Λογική για το όνομα της ομάδας
        country = m.get('country', '')
        team_name = "ΑΡΗΣ" if country == 'gr' else "ARIS"
        
        # Λογική για το ποιος είναι ο αντίπαλος και αν παίζουμε εντός/εκτός
        home = m.get('home_team', '')
        away = m.get('away_team', '')
        
        if home == "ARIS" or home == "ΑΡΗΣ":
            opponent = away
            is_home = True
        else:
            opponent = home
            is_home = False
            
        match_obj = {
            "date": m.get('date_time'), 
            "competition": m.get('tournament'),
            "stadium": m.get('stadium'), 
            "opponent": opponent,
            "team_name": team_name, # Αυτό το στέλνουμε στο HTML
            "is_home": is_home,     # Αυτό το στέλνουμε στο HTML
            "scoreA": m.get('home_score'), 
            "scoreB": m.get('away_score'),
            "sport": m.get('sport')
        }
        
        if m.get('status') == 'open': upcoming.append(match_obj)
        elif m.get('status') == 'close': completed.append(match_obj)
        
    return templates.TemplateResponse(request=request, name="sport.html", context={
        "upcoming": upcoming, 
        "completed": completed, 
        "sport": sport_name
    })



if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
