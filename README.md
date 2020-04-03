# DiscGenius
Introducing the digital DJ, now called DG (Disc Genius). A tool for creating DJ-Style transitions between techno tracks.

Dies ist ein Gruppenprojekt für den Kurs 'Independent Coursework I' im Master 'Angewandte Informatik' an der HTW Berlin.
Wir wollen automatisch Übergänge zwischen Techno Songs erzeugen, die harmonisch und nahtlos klingen. Der derzeitige Markt bietet hauptsächlich Crossfade-Übergänge an, die an gefühlt wahllosen Zeitpunkten stattfinden und klanglich nicht befriedigen.
Lediglich Spotify hat für ein paar vorgefertigte Playlists einen guten Algorithmus, der gute Übergänge erzeugt (https://djtechtools.com/2018/03/12/spotify-now-auto-mixing-tracks-in-playlists-gets-phrasing-right-usually/)

Unser Ziel ist es, mithilfe einer Analyse zwei zu mixender Tracks die Segmente/Phrasen im Song zu identifizieren. 
Bei elektronischer Musik sind diese meistens ein Vielfaches von vier Takten (16 Beats). 
Der Übergang soll so gestaltet werden, dass nicht nur die Beats der beiden Songs angepasst/synchronisiert werden, sondern auch die Segmente.

Wir wollen dem Benutzer verschiedene Übergangsszenarien anbieten, aus denen er auswählen kann. 
Nach der Analyse soll die Auswertung geschehen, in der für die verschiedenen Szenarien ein geeigneter Zeitpunkt gewählt wird und letztendlich der Übergang ausgeführt wird.

Die im Ordner befindliche Datei ```DiscGenius.postman_collection.json``` kann in die Postman-Applikation importiert werden, um ein Beispielsatz an Anfragen für den Webserver zu erhalten.

## Setup

You will need python3 and pip. After that you can start the application with running the script ```./run_api.sh```.
For audio file conversion you will need 'ffmpeg' (which is already included in the repo, ```https://ffmpeg.org/```) and 'LAME' which can be downloaded here ```http://lame.sourceforge.net/```.

The different mix scenarios for a transition are declared under ``/scenarios``. 

Currently we provide 7 different scenarios: ``CF_1.0, EQ_1.0, EQ_1.1, EQ_2.0, EQ_2.1, VFF_1.0, VFF_1.1``

It should automatically install the required python modules. After that the app is available under ```localhost:9001```.
The app provides the following API's (you can also check the auto-generated docs under ```localhost:9001/docs```):

```
GET /songs       -   See all available songs on the server which you can use to create a mix
GET /mixes       -   See all available mixes on the server which you can download.
GET /scenarios   -   See all available scenarios that you can chose from to create a mix.
GET /getMix      -   Download a created mix. Required query param: 'name'.
                 -   Example: localhost:9001/getMix?name=my_personal_mix.mp3
```

```
POST /upload     -   Upload a song to the server. Required query parameters: 'filename', 'extension' & 'bpm'. The 'filename' should not contain the audio format.
                 -   Example: localhost:9001/upload?filename=Dusty Kid - Sysma (Original Mix)&extension=wav&bpm=128.0

POST /createMix  -   Start the process of analysing and mixing two given songs. Required body parameters: 'song_a_name', 'song_b_name', 'scenario_name'. 
                 -   Optional parameters: 'bpm', 'mix_name', 'transition_length', 'transition_midpoint', 'transition_points'
                 -   Example body: 
                     {
                     	"song_a_name": "Dok & Martin - Andromeda (Original Mix)_130.0.wav",
                     	"song_b_name": "Hell Driver - 86 (Original Mix)_130.0.wav",
                     	"scenario_name": "EQ_1.0",
                     	"mix_name": "andromeda_to_86",
                     	"bpm": 130,
                        "transition_length": "64",
                        "transition_midpoint": "32"
                     }

                 -   You can skip the analysis when providing the 'transition_points' yourself. 'transition_length' & 'transition_midpoint' are then obsolete and will be calculated out of the given points.
                 -   Example body: 
                     {
                     	"song_a_name": "Dok & Martin - Andromeda (Original Mix)_130.0.wav",
                     	"song_b_name": "Hell Driver - 86 (Original Mix)_130.0.wav",
                     	"scenario_name": "EQ_1.0",
                     	"mix_name": "andromeda_to_86_manual",
                     	"bpm": 130,
                        "transition_points": {
                            "a": 15.115,
                            "c": 324.95,
                            "d": 384.02,
                            "e": 443.10
                        }
                     }

POST /adjustTempo -   Adjusts the tempo (bpm) of an existing song and saves a copy of that. 
                  -   Example body: 
                      {
                        "song_name": "Dok & Martin - Andromeda (Original Mix)_130.0.wav",
                        "bpm": 128.0
                      }
```





