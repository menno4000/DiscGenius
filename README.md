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

## Analyse (Max)

Die Analyse muss die folgenden Aufgaben bewältigen:
* BPM Ermittlung
* Audiodatei in Frequenzspektrum wandeln, mithilfe der Fast-Fourier-Transformation (FFT)
* Lautstärke des Songs bestimmen
* Analyse von 4-Beat-Segmenten auf verschiedene Aspekte:
    * Aktivität im Frequenzspektrum (High's, Mid's & Low's)
    * Vorhandensein durchgängiger Kick Drum -> dadurch können Breaks identifiziert werden & Beatmatching ist möglich
* zusammengehörige 4-Beat-Segmente zusammenfassen, um längere Segmente zu kreieren (optimalerweise 64-Beat-Segmente/16 Takte) 
* Generieren eines 'Transition-Scores' pro Segment. (Dieser berücksichtigt Aspekte, wie: Kick-Drum, Aktivität im Frequenzspektrum, Zeitpunkt im Track etc.)
 

## Evaluation & Anwendung (Oskar)

In diesem Part sollen die zwei analysierten Tracks ausgewertet werden. Um die Schemata sinnvoll anzuwenden, wird der Transition-Score der einzelnen Segmente benutzt.
Durch die "klassichen Instrumente" eines Mixers (3-Band-EQ, Volume- & Crossfader) soll der Übergang ausgeführt werden und die Audiodateien miteinander verschmolzen werden.

Der Algorithmus muss folgende Aufgaben erledigen:
* BPM-Sync
* Beatmatching
* "Segment-Sync"
* Bedienen der Elemente eines Mixers
* Aufzeichnen der veränderten Parameter

Der Verlauf der Parameter soll aufgezeichnet und gespeichert werden, um den Übergang in einer Web-Applikation abspielen und grafisch darstellen zu können.






