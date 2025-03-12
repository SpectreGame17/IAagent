import spotipy
import re
import os 
from spotipy.oauth2 import SpotifyOAuth
from dotenv import load_dotenv

env_path = os.path.join("config", ".env")
load_dotenv(env_path)

# Configurazione delle credenziali di Spotify
CLIENT_ID = os.getenv("SPOTIFY_ID")
CLIENT_SECRET = os.getenv("SPOTIFY_SECRET")
REDIRECT_URI = os.getenv("SPOTIFY_URI")

# Scopes necessari per controllare la riproduzione e accedere alle playlist dell'utente
SCOPE = 'user-read-playback-state user-modify-playback-state playlist-read-private'

# Ottieni il percorso assoluto della directory del progetto
project_dir = os.path.dirname(os.path.abspath(__file__))

# Unisci la directory del progetto con "__pycache__" per ottenere il percorso completo
CACHE = os.path.join(project_dir, "__pycache__", ".cache")

# Creazione del client Spotify
sp = spotipy.Spotify(auth_manager=SpotifyOAuth(client_id=CLIENT_ID,
                                               client_secret=CLIENT_SECRET,
                                               redirect_uri=REDIRECT_URI,
                                               scope=SCOPE,
                                               cache_path=CACHE))

def play_next():
    """
    Salta alla traccia successiva.
    """
    try:
        sp.next_track()
        print("Traccia successiva avviata.")
    except Exception as e:
        print("Errore nello spostarsi alla traccia successiva:", e)

def play_previous():
    """
    Torna alla traccia precedente.
    """
    try:
        sp.previous_track()
        print("Traccia precedente avviata.")
    except Exception as e:
        print("Errore nello spostarsi alla traccia precedente:", e)

def play_link(link):
    """
    Riproduce il contenuto specificato dal link Spotify.
    Supporta: brani, album, playlist e episodi (podcast).
    
    Il link deve essere nel formato:
      https://open.spotify.com/{tipo}/{id}
    dove {tipo} può essere track, album, playlist o episode.
    """
    try:
        # Estrazione del tipo e dell'ID dalla URL
        pattern = r'open\.spotify\.com/(?P<type>track|album|playlist|episode)/(?P<id>[a-zA-Z0-9]+)'
        match = re.search(pattern, link)
        if match:
            content_type = match.group("type")
            content_id = match.group("id")
            spotify_uri = f'spotify:{content_type}:{content_id}'
            
            if content_type in ["track", "episode"]:
                # Per brani ed episodi, passiamo il URI nella lista 'uris'
                sp.start_playback(uris=[spotify_uri])
                print(f"Riproduzione in corso: {spotify_uri}")
            elif content_type in ["album", "playlist"]:
                # Per album e playlist, usiamo il parametro 'context_uri'
                sp.start_playback(context_uri=spotify_uri)
                print(f"Riproduzione del contesto: {spotify_uri}")
            else:
                print("Tipo di contenuto non supportato.")
        else:
            print("Link non valido.")
    except Exception as e:
        print("Errore nella riproduzione del contenuto:", e)

def get_user_playlists():
    """
    Ottiene la lista delle playlist dell'utente.
    
    Restituisce una lista di dizionari con nome, ID e link della playlist.
    """
    try:
        playlists_data = sp.current_user_playlists()
        playlists = []
        for item in playlists_data['items']:
            playlist_info = {
                'name': item['name'],
                'id': item['id'],
                'link': item['external_urls']['spotify']
            }
            playlists.append(playlist_info)
        return playlists
    except Exception as e:
        print("Errore nel recupero delle playlist:", e)
        return []

def get_playlist_link(playlist_id):
    """
    Ottiene il link pubblico di una playlist dato il suo ID.
    """
    try:
        playlist = sp.playlist(playlist_id)
        link = playlist['external_urls']['spotify']
        return link
    except Exception as e:
        print("Errore nel recupero del link della playlist:", e)
        return None

def search_song(query):
    """
    Cerca una canzone o playlist su Spotify in base alla query e restituisce informazioni sul primo risultato.
    
    Restituisce un dizionario contenente il nome, l'artista (per tracce) e il link.
    """
    try:
        results = sp.search(q=query, type='track,playlist', limit=1)  # Cerca sia tracce che playlist
        tracks = results.get('tracks', {}).get('items', [])
        playlists = results.get('playlists', {}).get('items', [])

        if tracks:  # Se ci sono tracce
            track = tracks[0]
            song_info = {
                'name': track['name'],
                'artist': track['artists'][0]['name'],
                'link': track['external_urls']['spotify']
            }
            return song_info
        elif playlists:  # Se ci sono playlist
            playlist = playlists[0]
            playlist_info = {
                'name': playlist['name'],
                'link': playlist['external_urls']['spotify']
            }
            return playlist_info
        else:
            print("Nessun risultato trovato per la ricerca.")
            return None
    except Exception as e:
        print("Errore nella ricerca:", e)
        return None


def stop_playback(sp):
    """
    Ferma la riproduzione della musica in corso.
    :param sp: oggetto spotipy.Spotify già autenticato
    """
    sp.pause_playback()
    print("Riproduzione fermata.")

