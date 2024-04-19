from typing import Optional

from openai import OpenAI
from pydantic import BaseModel

from src import utils
from src.settings import get_settings

TASK_NAME: str = "optimaldb"
settings = get_settings()
client: OpenAI = OpenAI(api_key=settings.openai_api_key)

opti_db = """
Zygfryd: Wygrana nagroda za innowacyjność w JavaScript, Ukulele - ulubiony instrument, Hodowla rzadkich storczyków, Pasja do łamigłówek logicznych, Ulubiona gra planszowa: "Terra Mystica", Wędrówka po górach, Bycie mistrzem ortografii, Pierwsze miejsce w maratonie programistycznym, Ulubiony film: "Matrix", Znany z doskonałego poczucia humoru, Preferencja kolorystyczna: niebieski, Warsztaty kulinarnie promujące zdrowe odżywianie, Początki nauki gry na skrzypcach, Fan piłki nożnej, Kolekcja zegarków, Nauka nowych języków, Pionierstwo w Vue.js, Założyciel klubu programistycznego, Ulubiony taniec weselny: tango, Wybór zielonej herbaty zamiast kawy, Certyfikaty z różnych języków programowania, Bycie gitarzystą w zespole rockowym, Kolekcja powieści science fiction, Weekendowe wycieczki rowerowe, Ćwiczenia aikido, Prezenty w postaci nowych gadżetów, Ulubione gry wideo: strategiczne RPGi, Hobby modelarstwa, Aplikacja informująca o Międzynarodowej Stacji Kosmicznej, Blogowanie jako mentor programistyczny, Nagroda branżowa dla startupu, Organizacja festynu grillowego, Kreatywne pomysły podczas burz mózgów, Ucieczka od cyfrowego świata, Biegła znajomość języka migowego, Hobby enologiczne, Pomoc przy naprawie komputerów, Umiejętności rysowania i projektowania, Pasja do surfowania, Tworzenie etycznych algorytmów, Poszukiwanie życia pozaziemskiego, Kreatywność o świcie, Warsztaty kodowania dla dzieci, Konstruowanie dronów, Tworzenie otwartej platformy edukacyjnej, Tłumaczenie dokumentacji technicznej, Recenzowanie książek JavaScript, Doświadczenie w pracy dla start-upów i korporacji, Zaskakujące sztuczki karciane, Wspieranie współpracowników w trudnych momentach, Kolekcjonowanie starodruków, Encyklopedyczna wiedza, Praca jako barista, Wyczucie trendów w projektowaniu interfejsów użytkownika, Pomaganie młodym pasjonatom informatyki, Stworzenie biblioteki JavaScript, Rejestracja pomysłów w dzienniku kreatywnym, Aplikacja do obserwowania faz księżyca, Demotywatory z cytatami o programowaniu, Życie imprezy, Mistrz gier VR.
###
Stefan: Stefan organizuje konkurs hot dogów w sklepie, Pracuje w sklepie "Żabka", po pracy chodzi na siłownię, potrafi podnieść sztangę o własnej masie, Marzy o własnej siłowni z hot dogami, Tatuaż jamnika symbolizuje miłość do psa, Dochód ze sprzedaży idzie na schronisko, Doradza klientom w wyborze sosu, Zajął trzecie miejsce w zawodach, Prowadzi blog o treningach bicepsów, Sprzedawca Miesiąca pięć razy, Miłość do hot dogów z dzieciństwa, Sprzedaje autorskie hot dogi na festiwalach, Tajemnicza mieszanka przypraw w hot dogach, Planuje zawody w wyciskaniu sztangi, Monitoruje postępy na siłowni mierząc obwód bicepsa, Na urodziny dostaje gadżety kulturystyczne, Uratował kotka na drzewie, Kolekcja rękawic do treningu, Eksperymentuje z nowymi sosami, Znany jako "Król Hot Dogów" na siłowni, Święta bez hot dogów są niepełne, Szybkie pakowanie zakupów dla klientów, Marzy o hot dogu morskim, Ulubione filmy o kulturystach, Pomaga w organizacji eventów sportowych, Balans smaków w hot dogach to jego talent, Zestaw ciężarów na treningi na świeżym powietrzu, Hot dogi zawsze świeże i wysokiej jakości, Grilluje na spotkaniach rodzinnych, Doradza w ćwiczeniach na ramiona, Trenuje nowych pracowników, Zna niemieckie słowa o hot dogach, Pisze książkę o hot dogach, Uczestniczył w tworzeniu najdłuższego hot doga, Gościł w programie o hot dogach, Dzieli się wskazówkami żywieniowymi, Tatuaż jamnika przynosi szczęście, Często przebiera się za jamnika, Tytuł "Król Hot Dogów" potwierdzany uśmiechem, Eksperymentuje z wersjami tematycznymi, Dzieli się ciekawostkami o hot dogach, Ekspert w wyborze chlebka do hot doga, Trenuje początkujących na siłowni, Podaje hot dogi z kolorowymi sosami, Sylwetka wynik ciężkiej pracy, Seniorzy rozmawiają o zdrowiu z nim, Szybko wydaje resztę klientom, Ozdabia linię hot dogów w sklepie, Często bierze udział w konkursach, Dostarcza posiłki na zawody siłowe, Słynie z obsługi klienta, Zna pierwszą pomoc, Dzieci proszą o baloniki jamników, Prowadzi punkt z hot dogami na wydarzeniach, Miał epizod kulturystyczny, Słucha audiobooków po treningu, Lubuje się w rywalizacji sprzedawców, Eksperymentuje z lokalnymi przysmakami.
###
Ania: organizuje konferencje prawnicze w czasie studiów, Ania prowadzi kanał na YouTube o beauty, Ania zdobywa doświadczenie w kancelarii prawnej latem, Ania imponuje umiejętnościami za kierownicą Porsche, Ania regularnie startuje w zawodach fitness bikini, Ania eksponuje czerwoną pomadkę w mediach społecznościowych, Ania gotuje zdrowe i smaczne posiłki dla przyjaciół, Ania angażuje się w zarządzanie kołem naukowym, Jennifer Lopez to inspiracja fitnessowa dla Ani, Ania prezentuje luksusowe akcesoria do włosów na Instagramie, Ania lubi legalne thrillery, Ania ubiera się profesjonalnie na stoku narciarskim, Ania organizuje warsztaty z samoobrony dla kobiet, Ania pomaga w lokalnym centrum praw kobiet, Porsche Ani ma personalizowany numer rejestracyjny, Ania relaksuje się w spa po trudnym tygodniu, Ania subskrybuje boksy kosmetyczne co miesiąc, Ania praktykuje prawo we Francji latem, Ania lubi klasyczne dramaty prawnicze, Ania interesuje się prawem medycznym, Ania została zaproszona do kampanii fitness, Ania biega regularnie w parku, Ania pracuje nad publikacją o cyberbezpieczeństwie, Ania nosi skórzany notatnik zawsze przy sobie, Ania uwielbia serum z witaminą C, Ania angażuje się w wymianę międzynarodową, Ania ma patriotyczne zdobienie w swoim Porsche, Ania zaprojektowała łuk prawny dla uczelni, Ania używa syntetycznych pędzli do makijażu, Ania nosi ażurowe sandały latem, Ania kolekcjonuje limitowane perfumy, Ania ma zaawansowany system audio w Porsche, Ania szydełkuje unikatowe akcesoria, Ania mówi płynnie po hiszpańsku, Ania odwiedza lokalne schronisko zwierząt, Ania przemawiała o prawach kobiet, Ania skomponowała własną piosenkę na gitarze, Ania angażuje się w projekt budowania marki osobistej, Ania tworzy unikalne kostiumy na Halloween, Ania medytuje i biega przed egzaminami, Ania korzysta z eleganckich teczek spraw, Ania gra w szachy w czasie przerw na uczelni, Ania udziela korepetycji z prawa konstytucyjnego, Ania ma duży tatuaż z symbolami na plecach.
"""


class TaskResponse(BaseModel):
    code: int
    msg: str
    answer: Optional[str] = None


def solve(task_name: str) -> None:
    token_url: str = utils.get_token_url(task_name)
    token: str = utils.get_token(token_url)
    task_url: str = utils.get_task_url(token)
    task_obj = TaskResponse(**utils.get_task(task_url).json())
    task_obj.answer = opti_db

    utils.send_answer(token=token, answer=task_obj.answer)


if __name__ == "__main__":
    # utils.print_task(TASK_NAME)
    solve(TASK_NAME)
