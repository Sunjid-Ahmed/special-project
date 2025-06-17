import time
import homepod
import pikud_haoref_api
import timeout

CATEGORIES = {}


def play_sound_loop(text, filename, volume=50):
    """
    prints alerts text and plays sound again in case homepod was busy
    :param text: text to print
    :param filename: sound file name
    :return: none
    """
    print(text)
    if homepod.play_alarm(filename, volume) == 1:
        time.sleep(1.5)
        homepod.play_alarm(filename, volume)  # trying again, in case homepod was busy


def play_local_alert(alert):
    """
    determines alert type and plays matching sound
    :param alert: parsed JSON of alert
    :return: none
    """
    category = int(alert["cat"])

    # alert data is the list of affected locations
    try:
        # early alert #
        if category == CATEGORIES["early_alert"]:
            play_sound_loop(str("EARLY ALERT" + alert["title"]), "early_warning.mp3", 65)

        # notification in the area #
        elif category == CATEGORIES["notification"]:
            play_sound_loop(str("NOTIFICATION" + alert["title"]), "early_warning.mp3", 65)

        # active alerts #
        elif category == CATEGORIES["rockets_and_missiles"]:
            play_sound_loop(str("ROCKET ALERT:" + alert["title"]), "active_attack.mp3")

        elif category == CATEGORIES["terrorist_infiltration"]:
            play_sound_loop(str("TERRORIST INFILTRATION" + alert["title"]), "active_attack.mp3")

        elif category == CATEGORIES["cbrne"]:
            play_sound_loop(str("CHEMICAL/BIOLOGICAL/RADIOLOGICAL/NUCLEAR/EXPLOSIVE:" + alert["title"]),
                            "active_attack.mp3")

        # if no category fits
        else:
            play_sound_loop(str("ALERT" + alert["title"]), "active_attack.mp3")
    
    # in case of a parsing error
    except Exception as e:
        print(e)
        play_sound_loop(str("UNKNOWN ALERT"), "early_warning.mp3", 65)

    time.sleep(2)  # waiting for homepod before the next play


def are_areas_affected(alert, areas):
    return any(x in alert["data"] for x in areas)


def alert_fetch_loop(areas, non_local_alerts=False):
    """
    continuously fetches alerts from Pikud Haoref api, parses them, and plays sound if necessary
    :param non_local_alerts: boolean, whether to sound alerts for areas not added to list
    :param areas: list of areas to play sound when alerted
    :return: None
    """
    non_local_timeout = timeout.Timeout()

    while True:
        time.sleep(1.1)
        alert = pikud_haoref_api.fetch_current_alert()
        print("alert: " + str(alert))

        # check if selected cities match the current alert and notify user
        if alert is not None and are_areas_affected(alert, areas):
            play_local_alert(alert)

        elif non_local_alerts and not non_local_timeout.is_timed_out():
            print("safe")
            if not non_local_timeout.is_timed_out():
                play_sound_loop(str("NON LOCAL ALERT" + alert["title"]), "non_local_alert.mp3", 15)
                non_local_timeout.set_timeout()
        else:
            print("safe")
            non_local_timeout.cycle_timout()

        if alert is None:
            # setting it to 0 since the alert is over, and next time there is one it is delivered immediately
            non_local_timeout.reset_timeout()


def add_cities():
    areas = ["ברחבי הארץ"]

    choice = input("Do you wish to add cities? y/n ")

    if choice.lower() == "y":
        city = ""
        print("--To stop adding cities enter done--")
        while city != "done":
            city = input("Enter city name in hebrew (make sure spelling is right, you may add multiple spellings) ")
            if city != "done":
                areas.append(city)

    return areas


def main():
    global CATEGORIES

    areas = add_cities()
    print(areas)

    CATEGORIES = pikud_haoref_api.fetch_and_map_categories()
    print(CATEGORIES)

    answer = input("do you want non-local alerts to sound too? y/n ")
    if answer.lower() == "y":
        alert_fetch_loop(areas, True)
    else:
        alert_fetch_loop(areas, False)


if __name__ == "__main__":
    main()
