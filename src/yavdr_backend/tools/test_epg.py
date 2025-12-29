from . import epg

epg_data = """C T-8468-12547-801 BR Fernsehen Nord HD
E 13233 1632467700 2700 4F 1E
T Querbeet Classix
D Themen:|* Hausbäume für kleine Gärten|* Zwiebelblüher im Topf|* Pastinake für Babys|* Hostavielfalt auf dem Balkon|* Beruf Staudengärtner|* 25 Jahre Landesgartenschau Dinkelsbühl|* Küchengarten von Schloss Hof in Österreich
G 90
X 3 01 deu Teletext-Untertitel
V 1632467700
e
c
C T-8468-12291-770 arte HD
E 9408 1632470100 3300 4E 17
T Öl. Macht. Geschichte (1/2)
S Aufstieg und Fall
D Die Entdeckung des Erdöls glich einem Wunder: Petroleumlampen erhellten Wohnzimmer wie nie zuvor, ölbetriebene Maschinen arbeiteten so effektiv wie 50 Arbeitskräfte. Seine Kraft bescherte der Menschheit ein nie gekanntes Wirtschaftswachstum. John D. Rockefeller wurde durch Öl zum ersten Milliardär der Geschichte. Aber der Rohstoff sollte zwei Weltkriege entscheidend beeinflussen.|Anhand zahlreicher Fundstücke aus internationalen Archiven und mittels Interviews entsteht ein vielschichtiges Porträt eines Rohstoffs, der über viele Jahrzehnte - und bis heute unverändert - unseren Alltag prägt.
G 80 82
R 6
X 3 01 deu Teletext-Untertitel
V 1632470400
e
E 9409 1632473400 3300 4E 17
T Öl. Macht. Geschichte (2/2)
S Gier und Verderben
D Macht und Erdöl sind untrennbar verbunden. Als wichtigste Energiequelle bestimmt Erdöl über Aufschwung und Niedergang, über Konsum, Armut und Kriege. Wie das schwarze Gold bestehende Machtverhältnisse über Nacht verändern kann, bekam der Westen 1973 zu spüren: Die OPEC verringert die gelieferte Ölmenge als Strafe für die Einmischung in den arabisch-israelischen Krieg. Plötzlich machte Öl Politik. Damals hatte man es versäumt, Technologien für den Einsatz erneuerbarer Technologien zu entwickeln.
G 80 82
R 6
X 3 01 deu Teletext-Untertitel
V 1632473400
e
E 9410 1632476700 1800 50 16
T 42 - Die Antwort auf fast alles
S Können wir uns durch die Erdkugel graben?
D "42 - Die Antwort auf fast alles" ist die neue Wissensserie von ARTE, die durch große und kleine Fragen der Menschheit navigiert, originell, assoziativ, um die Ecke gedacht und getragen von einer prägnanten Stimme: Nora Tschirner macht sich Gedanken, sammelt Informationen, ordnet Material und gibt uns den Durchblick.|In dieser Folge: Wir fliegen hoch hinaus, erkunden das Weltall, aber was ist mit der anderen Richtung? Unter unseren Füßen herrscht im wahrsten Sinne des Wortes Dunkelheit. Geologen zitieren gerne den Bergmannsspruch: "Vor der Hacke ist es duster." Und so ist es.
X 3 01 deu Teletext-Untertitel
V 1632476700
e
c"""

def test_channel_parsing():
    assert epg.parse_channel("C T-8468-12547-801 BR Fernsehen Nord HD") == ("T-8468-12547-801", "BR Fernsehen Nord HD")

def test_epg_event_parsing():
    assert epg.parse_event("E 9409 1632473400 3300 4E 17") == (9409, 1632473400, 3300, 0x4E, 0x17)
