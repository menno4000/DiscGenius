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

Unsere Gedanken & Notizen sind hier festgehalten: https://tinyurl.com/yy4fbkgz


## Setup

You will need python3 and pip. After that you can start the application with running the script ```./run_api.sh```.
For audio file conversion you will need 'ffmpeg' (which is already included in the repo, ```https://ffmpeg.org/```) and 'LAME' which can be downloaded here ```http://lame.sourceforge.net/```.

It should automatically install the required python modules. After that the app is available under ```localhost:9001```.
The app provides the following API's:

```
GET /songs       -   See all available songs on the server which you can use to create a mix
GET /mixes       -   See all available mixes on the server which you can download.
GET /scenarios   -   See all available scenarios that you can chose from to create a mix.

POST /upload     -   Upload a song to the server. Required query parameters: 'filename' & 'extension'
POST /createMix  -   Start the process of analysing and mixing two given songs. Required body parameters: 'song_a_name', 'song_b_name', 'scenario_name'. Optional parameters: 'mix_name'.

GET /getMix      -   Download a created mix. Required query param: 'name'.
```





