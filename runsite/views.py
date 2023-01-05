from django.shortcuts import render
from .forms import getData, getTraningInfo
import requests
from bs4 import BeautifulSoup
from datetime import date, datetime
import folium
import geocoder
# Create your views here.


runs = {}


def calculate_difference(key):
    run_date_str = runs[key]["date"][:10] + " 0:0:0"
    today = datetime.now()

    run_day = datetime.strptime(run_date_str, "%Y-%m-%d %H:%M:%S")
    difference = (run_day - today).days
    minus = 0
    if today.weekday() != 0:
        minus += 7 - today.weekday()

    return difference - minus


def calculate_distance(key):
    distance = ''
    i = 0
    while runs[key]["distance"][i] != "k":
        distance += runs[key]["distance"][i]
        i += 1
    return int(distance)


def calculate_speed(hour, minutes, distance):
    minutes += hour*60
    speed = minutes / distance
    return speed


def speed_to_str(speed):
    minutes = speed // 1
    sek = speed - minutes
    sek *= 60
    if sek < 10:
        sek = "0" + str(round(sek))
    else:
        sek = str(round(sek))
    minutes = str(round(minutes))
    return minutes + ":" + sek


def basic_introduction(weeks):

    plan4 = {
        '1': {'pon': 'odpoczynek', 'wt': 'bieg 10 min', 'sr': 'opdoczynek', 'czw': 'bieg 10 min', 'pt': 'odpoczynek',
              'weekend': 'bieg 15 min'},
        '2': {'pon': 'odpoczynek', 'wt': 'bieg 15 min', 'sr': 'opdoczynek', 'czw': 'bieg 15 min', 'pt': 'odpoczynek',
              'weekend': 'bieg 20 min'},
        '3': {'pon': 'odpoczynek', 'wt': 'bieg 20 min', 'sr': 'opdoczynek', 'czw': 'bieg 25 min', 'pt': 'odpoczynek',
              'weekend': 'bieg 25 min'},
        '4': {'pon': 'odpoczynek', 'wt': 'bieg 25 min', 'sr': 'opdoczynek', 'czw': 'bieg 30 min', 'pt': 'odpoczynek',
              'weekend': 'bieg 30 min'}}

    plan5 = {
        '1': {'pon': 'odpoczynek', 'wt': 'bieg 10 min', 'sr': 'opdoczynek', 'czw': 'bieg 10 min', 'pt': 'odpoczynek',
              'weekend': 'bieg 10 min'},
        '2': {'pon': 'odpoczynek', 'wt': 'bieg 15 min', 'sr': 'opdoczynek', 'czw': 'bieg 15 min', 'pt': 'odpoczynek',
              'weekend': 'bieg 15 min'},
        '3': {'pon': 'odpoczynek', 'wt': 'bieg 20 min', 'sr': 'opdoczynek', 'czw': 'bieg 20 min', 'pt': 'odpoczynek',
              'weekend': 'bieg 20 min'},
        '4': {'pon': 'odpoczynek', 'wt': 'bieg 25 min', 'sr': 'opdoczynek', 'czw': 'bieg 25 min', 'pt': 'odpoczynek',
              'weekend': 'bieg 25 min'},
        '5': {'pon': 'odpoczynek', 'wt': 'bieg 30 min', 'sr': 'opdoczynek', 'czw': 'bieg 30 min', 'pt': 'odpoczynek',
              'weekend': 'bieg 30 min'}}

    plan2 = {
        '1': {'pon': 'odpoczynek', 'wt': 'bieg 10 min', 'sr': 'opdoczynek', 'czw': 'bieg 15 min', 'pt': 'odpoczynek',
              'weekend': 'bieg 15 min'},
        '2': {'pon': 'odpoczynek', 'wt': 'bieg 15 min', 'sr': 'opdoczynek', 'czw': 'bieg 20 min', 'pt': 'odpoczynek',
              'weekend': 'bieg 30 min'},
    }
    if weeks == 4:
        return plan4, weeks - 4, 5
    elif weeks == 5:
        return plan5, weeks - 5, 6
    else:
        print("tu jestem")

        return plan2, 2, 3


def introduction(weeks, actual_week, distance, week, mode, plan, weeks_for_introduction=0):

    mins = 0
    if mode == "Basic":
        # pocztatkowy dystans dla basic
        mins = 2
        if distance < 11:
            if weeks_for_introduction == 0:
                # ilosc tygodni na dostosowanie dystansu
                weeks_for_introduction = 4

        elif distance < 22:
            if weeks_for_introduction == 0:
                weeks_for_introduction = 10

        else:
            if weeks_for_introduction == 0:
                weeks_for_introduction = 15
            # jako ze dystans jest bardzo duzy trening odbywa sie na max 3/4 jego wartosic
            distance *= 0.75

    if mode == "Medium":
        mins = 5
        if distance < 22:
            if weeks_for_introduction == 0:
                weeks_for_introduction = 4
        else:
            if weeks_for_introduction == 0:
                weeks_for_introduction = 10
            distance *= 0.75

    if mode == "Advance":
        mins = 10
        if weeks_for_introduction == 0:
            weeks_for_introduction = 10
        distance *= 0.75


    # ilosc kilometrow jaka zwiekszamy co kazdy tydzien
    jump = (distance - mins) / (weeks_for_introduction - 1)

    # iterowanie przez kazdy tydzien traningu wprowadzajacego
    for i in range(actual_week, actual_week + weeks_for_introduction):
        plan[str(i)] = {}
        weeks -= 1
        # iterowanie przez kazdy dzien tygodnia (weekend jako 1 dzien czyli mozna se wybrac sob lub nd)
        for day in range(0, len(week)):
            if day % 2 == 0:
                plan[str(i)][week[day]] = "odpoczynek"
            elif (day == 1 or day == 3) and mins > 5:
                plan[str(i)][week[day]] = "bieg na " + str(round(mins / 2)) + "km"
            else:
                plan[str(i)][week[day]] = "bieg na " + str(round(mins)) + "km"
        mins += jump

    #aktualizowanie aktualnego tygonia
    actual_week += weeks_for_introduction

    return plan, weeks, actual_week


def full_training(weeks, actual_week, distance, week, mode, plan, speed):
    # range (actual_week, actual_week + weeks)

    if mode == "Basic":

        # min predkosc po introduction ktora jest zwiekszana z klejnymi tygodniami
        min_speed = 10
        if distance >= 22:
            distance *= 0.75

    elif mode == "Medium":
        min_speed = 8
        if distance >= 22:
            distance *= 0.75

    else:
        min_speed = 7
        if distance >= 22:
            distance *= 0.75

    # zwiekszanie predkosci co tydzien o jump
    jump = (min_speed - speed) / weeks
    for i in range(actual_week, actual_week + weeks):
        plan[str(i)] = {}
        min_speed -= jump
        weeks -= 1
        actual_week += 1
        for day in range(0, len(week)):
            if day % 2 == 0:
                plan[str(i)][week[day]] = "odpoczynek"
            elif day == 1 and 5 < distance < 11:
                plan[str(i)][week[day]] = "bieg na " + str(round(distance / 2)) + "km w czasie " + \
                                          speed_to_str(min_speed * 0.5) + " min/km"
            elif day == 1 and 5 < distance < 22:
                plan[str(i)][week[day]] = "bieg na " + str(round(distance / 2)) + "km w czasie " + \
                                          speed_to_str(min_speed * 0.7) + " min/km"
            elif day == 1 and 5 < distance:
                plan[str(i)][week[day]] = "bieg na " + str(round(distance / 2)) + "km w czasie " + \
                                          speed_to_str(min_speed * 0.9) + " min/km"
            elif day == 3 and mode != "Advance":
                plan[str(i)][week[day]] = "bieg interwalowy: 5x (bieg 1.5 min na maksimum mozliwosci + " \
                                          "2 min wolnego truchtu) + wybiganie na " + str(round(distance / 2)) + "km"
            elif day == 3:
                plan[str(i)][week[day]] = "bieg interwalowy: 5x (bieg 1.5 min na maksimum mozliwosci pod gorke + " \
                                          "2 min wolnego truchtu z gorki) + wybiganie na " + \
                                          str(round(distance / 2)) + "km"
            else:
                plan[str(i)][week[day]] = "bieg na " + str(distance) + "km w czasie " + speed_to_str(min_speed) + \
                                          " min/km"

    return plan, weeks, actual_week


def home(request):
    global runs
    runs = {}
    if request.method == "POST":
        runs = {}

        # pobranie danych z forms po wcisnieciu przycisku
        form = getData(request.POST)

        # ustawienie zmiennej na global w celu modyfikacji dict runs
        if form.is_valid():

            # pobieranie danych
            city = form.cleaned_data["city"]
            date_from_wrong = form.cleaned_data["date_from"]
            date_to_wrong = form.cleaned_data["date_to"]
            distance_from = form.cleaned_data["distance_from"]
            distance_to = form.cleaned_data["distance_to"]

            # zamiana daty
            if date_from_wrong is not None:
                date_from_correct = str(date_from_wrong.year) + "-" + str(date_from_wrong.month) + "-" + \
                                    str(date_from_wrong.day)
            else:
                date_from_correct = ""

            if date_to_wrong is not None:
                date_to_correct = str(date_to_wrong.year) + "-" + str(date_to_wrong.month) + "-" + \
                                    str(date_to_wrong.day)
            else:
                date_to_correct = ""

            # wyczyszczenie input-ow
            form = getData()

            # pobranie danych ze strony
            url = "https://run-log.com/events/?terms=" + city + "&date_from=" + date_from_correct + \
                  "&date_to=" + date_to_correct + "&distance_from=" + str(distance_from) + \
                  "&distance_to=" + str(distance_to) + "&location_radius=&action="
            website = requests.get(url)
            result = website.text
            doc = BeautifulSoup(result, "html.parser")
            table = doc.tbody
            trs = table.contents
            i = 0

            # iterowanie po kazdym elemenecie tabeli z danymi zawodow
            for tr in trs:
                i += 1

                # sprawdzenie czy w tabeli istenieja biegi oraz czy nie sprawdzania jest pusty wiersz
                if i % 2 == 0 and i <= 10 and len(tr.contents) >= 10:
                    run = {}
                    date, name, distance, shit, location = tr.contents[1::2]
                    run["date"] = date.text
                    run["distance"] = distance.text.strip()
                    run["location"] = location.text
                    run["number"] = i/2
                    name = name.a.string

                    # wyszukiwanie linkow do obrazu dla kazdego miasta w ktorym jest bieg
                    r = requests.get(
                        'https://commons.wikimedia.org/w/index.php?search=' + run["location"]
                        + '&title=Special:MediaSearch&go=Go&type=image')
                    result = r.text
                    doc = BeautifulSoup(result, "html.parser")
                    images = doc.find('a', {'class': 'sdms-image-result'})
                    print(images)
                    if not images:
                        run["image"] = "#"
                    else:
                        r = requests.get(images['href'])
                        result = r.text
                        doc = BeautifulSoup(result, "html.parser")
                        doc2 = doc.find('div', {'class': 'mw-body-content'})
                        image = doc2.find('img')
                        run["image"] = image['src']

                    # w wypadku wystapnie biegu z taka sama nazwa dodanie numerka do nazyw
                    if name in runs:
                        runs[name+" ("+str(i/2)[0]+")"] = run
                    else:
                        runs[name] = run
    else:
        form = getData()
    return render(request, "runsite/home.html", {"Data": form, "Runs": runs})


def run_plan(request):

    # pobranie url storny (zawiera index dictionary z dpowiednimi zawodami)
    url = int(request.build_absolute_uri()[22])
    key = list(runs.keys())[url-1]
    working = 1
    # oblicznie ile dni oraz tygodni jest do zawodow
    days = calculate_difference(key)
    weeks = days//7
    week = ['pon', 'wt', 'sr', 'cw', 'pt', 'weekend']
    plan = {}
    # konwertowanie dystansu ze slownika na typ int (pomijanie metrow)
    distance = calculate_distance(key)

    # generowanie mapy ze znacznikiem lokalizacji biegu
    try:
        location = geocoder.location(runs[key]['location'])
        lat = location.lat
        lng = location.lng
        mapa = folium.Map(location=[lat, lng], zoom_start=12)
        folium.Marker([lat, lng]).add_to(mapa)
    except:
        location = geocoder.osm('PL')
        lat = location.lat
        lng = location.lng
        mapa = folium.Map(location=[lat, lng], zoom_start=12)

    mapa = mapa._repr_html_()
    if request.method == "POST":
        working = 1

        # pobranie danych z forms po wcisnieciu przycisku
        form = getTraningInfo(request.POST)

        if form.is_valid():
            type_of_training = form.cleaned_data["type"]
            time_hours = form.cleaned_data["time_hours"]
            if time_hours:
                try:
                    time_hours = int(time_hours)
                except ValueError:
                    working = 0
                    time_hours = 0
            else:
                time_hours = 0
            time_minutes = form.cleaned_data["time_minutes"]
            if time_minutes:
                try:
                    time_minutes = int(time_minutes)
                except ValueError:
                    working = 0
                    time_minutes = 0
            else:
                time_minutes = 0
            speed = calculate_speed(time_hours, time_minutes, distance)
            if time_minutes < 0 or time_hours < 0 or speed < 2.5:
                working = 0

            form = getTraningInfo()
            if type_of_training == "Basic":
                speed *= 1.2
                if weeks <= 3:
                    print("nie da sie wygnerowa traningu1")
                    working = 0
                elif weeks <= 20:

                    #pierwszy tryb (najkrotrze zawody)
                    if distance < 11:
                        if weeks < 6:
                            plan, weeks, actual_week = basic_introduction(weeks)
                        elif weeks >= 6:
                            # pamietaj 6 - 2(basic_introduction)
                            # pamietaj ze full_training() z tych weekow co zostaly po introduction
                            plan, dif, actual_week = basic_introduction(2)
                            print(weeks)
                            # odjecie od pozostalych tygodni juz wykorzystanych
                            weeks -= dif
                            plan, weeks, actual_week = introduction(weeks, actual_week, distance, week,
                                                                    type_of_training, plan)
                            print(plan)
                            print(weeks)
                            print(actual_week)
                            plan, weeks, actual_week = full_training(weeks, actual_week, distance, week,
                                                                     type_of_training, plan, speed)
                            print(plan)
                            print(weeks)
                            print(actual_week)

                    #drugi tryb (srednio dlugie zaowdy)
                    elif distance < 22:
                        if weeks < 12:
                            print("nie da sie wygenerowac treningu2")
                            working = 0
                        elif weeks >= 12:

                            plan, dif, actual_week = basic_introduction(2)
                            weeks -= dif
                            print(weeks)
                            plan, weeks, actual_week = introduction(weeks, actual_week, distance, week,
                                                                    type_of_training, plan)
                            print(plan)
                            print(weeks)
                            print(actual_week)
                            plan, weeks, actual_week = full_training(weeks, actual_week, distance, week,
                                                                     type_of_training, plan, speed)
                            print(plan)
                            print(weeks)
                            print(actual_week)


                    #trzeci tryb(dlugie zawody)
                    else:
                        if weeks < 17:
                            print("nie da sie wygenerowac treningu2")
                            working = 0
                        if weeks >= 17:
                            plan, dif, actual_week = basic_introduction(2)
                            weeks -= dif
                            plan, weeks, actual_week = introduction(weeks, actual_week, distance, week,
                                                                    type_of_training, plan)

                            print(plan)
                            print(weeks)
                            print(actual_week)
                            plan, weeks, actual_week = full_training(weeks, actual_week, distance, week,
                                                                     type_of_training, plan, speed)
                            print(plan)
                            print(weeks)
                            print(actual_week)
                # ----------------------------------
                else:
                    if distance < 11:

                        # wyliczenie na korym tygoniu konczy sie introducion (+2 by uwzglednic basic_introdution)
                        weeks_for_introduction = round((weeks * 0.2)//1 + 2)
                        plan, dif, actual_week = basic_introduction(2)
                        weeks -= dif
                        plan, weeks, actual_week = introduction(weeks, actual_week, distance, week,
                                                                type_of_training, plan, weeks_for_introduction)

                        print(plan)
                        print(weeks)
                        print(actual_week)
                        plan, weeks, actual_week = full_training(weeks, actual_week, distance, week,
                                                                 type_of_training, plan, speed)
                        print(plan)
                        print(weeks)
                        print(actual_week)
                    elif distance < 22:
                        weeks_for_introduction = round((weeks * 0.5) // 1 + 2)
                        plan, dif, actual_week = basic_introduction(2)
                        weeks -= dif
                        plan, weeks, actual_week = introduction(weeks, actual_week, distance, week,
                                                                type_of_training, plan, weeks_for_introduction)

                        print(plan)
                        print(weeks)
                        print(actual_week)
                        plan, weeks, actual_week = full_training(weeks, actual_week, distance, week,
                                                                 type_of_training, plan, speed)
                        print(plan)
                        print(weeks)
                        print(actual_week)
                    else:
                        weeks_for_introduction = round((weeks * 0.75) // 1 + 2)

                        plan, dif, actual_week = basic_introduction(2)
                        weeks -= dif
                        plan, weeks, actual_week = introduction(weeks, actual_week, distance, week,
                                                                type_of_training, plan, weeks_for_introduction)
                        print(plan)
                        print(weeks)
                        print(actual_week)
                        plan, weeks, actual_week = full_training(weeks, actual_week, distance, week,
                                                                 type_of_training, plan, speed)
                        print(plan)
                        print(weeks)
                        print(actual_week)
            elif type_of_training == "Medium":
                if weeks <= 3:
                    print("nie da sie wygnerowa traningu1")
                    working = 0
                elif distance < 11:

                    # dla malego dystansu w trybie medium nie ma introduction
                    plan, weeks, actual_week = full_training(weeks, 1, distance, week,
                                                             type_of_training, {}, speed)
                    print(plan)
                    print(weeks)
                    print(actual_week)

                elif weeks <= 20:

                    if distance < 22:
                        if weeks < 4:
                            print("nie da sie wygnerowa traningu2")
                            working = 0
                        else:
                            plan, weeks, actual_week = introduction(weeks, 1, distance, week,
                                                                    type_of_training, {})
                            print(plan)
                            print(weeks)
                            print(actual_week)
                            plan, weeks, actual_week = full_training(weeks, actual_week, distance, week,
                                                                     type_of_training, plan, speed)
                            print(plan)
                            print(weeks)
                            print(actual_week)
                    else:
                        if weeks < 10:
                            print("nie da sie wygnerowa traningu2")
                            working = 0
                        else:
                            plan, weeks, actual_week = introduction(weeks, 1, distance, week,
                                                                    type_of_training, {})
                            print(plan)
                            print(weeks)
                            print(actual_week)
                            print(speed)
                            plan, weeks, actual_week = full_training(weeks, actual_week, distance, week,
                                                                     type_of_training, plan, speed)
                            print(plan)
                            print(weeks)
                            print(actual_week)
                else:
                    if distance < 22:
                        weeks_for_introduction = round((weeks * 0.2) // 1)
                        plan, weeks, actual_week = introduction(weeks, 1, distance, week,
                                                                type_of_training, {}, weeks_for_introduction)
                        print(plan)
                        print(weeks)
                        print(actual_week)
                        plan, weeks, actual_week = full_training(weeks, actual_week, distance, week,
                                                                 type_of_training, plan, speed)
                        print(plan)
                        print(weeks)
                        print(actual_week)
                    else:
                        weeks_for_introduction = round((weeks * 0.5) // 1)
                        plan, weeks, actual_week = introduction(weeks, 1, distance, week,
                                                                type_of_training, {}, weeks_for_introduction)
                        print(plan)
                        print(weeks)
                        print(actual_week)
                        plan, weeks, actual_week = full_training(weeks, actual_week, distance, week,
                                                                 type_of_training, plan, speed)
                        print(plan)
                        print(weeks)
                        print(actual_week)

            else:
                speed *= 0.9
                if weeks <= 3:
                    print("nie da sie wygnerowa traningu1")
                    working = 0
                elif distance < 22:

                    # dla malego dystansu oraz sredniego w trybie advance nie ma introduction
                    plan, weeks, actual_week = full_training(weeks, 1, distance, week,
                                                             type_of_training, {}, speed)
                    print(plan)
                    print(weeks)
                    print(actual_week)

                elif weeks < 10:
                    print("nie da sie wygnerowa traningu3")
                    working = 0
                elif weeks <= 20:

                    plan, weeks, actual_week = introduction(weeks, 1, distance, week,
                                                            type_of_training, {})

                    #print(plan)
                    print(weeks)
                    print(actual_week)
                    print(speed)
                    plan, weeks, actual_week = full_training(weeks, actual_week, distance, week,
                                                             type_of_training, plan, speed)
                    print(plan)
                    print(weeks)
                    print(actual_week)
                else:
                    weeks_for_introduction = round((weeks * 0.5) // 1)
                    plan, weeks, actual_week = introduction(weeks, 1, distance, week,
                                                            type_of_training, {}, weeks_for_introduction)
                    #print(plan)
                    print(weeks)
                    print(actual_week)
                    print(speed)
                    plan, weeks, actual_week = full_training(weeks, actual_week, distance, week,
                                                             type_of_training, plan, speed)
                    print(plan)
                    print(weeks)
                    print(actual_week)

        if working == 0:
            plan = {}
        for name, values in plan.items():
            print(name)
            print(values)
    else:
        form = getTraningInfo()
    return render(request, "runsite/runPlan.html", {"Forms": form, "Key": key, "Run": runs[key], "Mapa": mapa,
                                                    "Plan": plan, "Working": working})
