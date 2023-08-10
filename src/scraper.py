from ScrapeThread import ScrapeThread
import yaml

if __name__ == '__main__':
    cities = []
    start_date = 0
    end_date = 0

    # IMPORTANT
    # how many threads to use for web scraping
    # choosing an adequate number is necessary in order to not get errors during the scraping process
    WORKERS = 6

    with open("../webscrape_settings.yaml", "r") as stream:
        doc = yaml.safe_load(stream)
        
        cities = doc["flight_locations"]
        start_date = doc["start_date"]
        end_date = doc["end_date"]
        WORKERS = doc["WORKERS"]

        print(cities, start_date, end_date, WORKERS)

    # link to google flights
    url: str = "https://www.google.com/travel/flights?tfs=CBwQARoaEgoyMDIzLTEwLTA4agwIAhIIL20vMGZ0anhAAUgBcAGCAQsI____________AZgBAg&hl=en-GB&curr=EUR"

    # in case you just want to scrape few flights
    destinations = [
        ("Sofia", "Eindhoven", "23 Aug"), 
        ("Canada", "Rome", "23 Aug"),
        ("Canada", "Rome", "2 Sep")
    ]

    # in case you want to scrape all flights between a pair of cities in the list
    cities = [
        "Sofia",
        "Eindhoven",
        "Paris",
        "Rome",
        "Lisbon",
        "Bucharest",
        "Budapest",
        "Copenhagen",
        "Amsterdam",
        "Berlin"
    ]

    delegated_work = [[] for i in range(WORKERS)]

    k = 0
    for city_1 in cities:
        for city_2 in cities:
            if city_1 != city_2:
                for date in range(start_date, end_date + 1):
                    delegated_work[k].append((city_1, city_2, date))
                    k += 1
                    k %= WORKERS

    all_threads = []
    for x in delegated_work:
        t = ScrapeThread(url, x)
        t.start()

        all_threads.append(t)
    for t in all_threads:
        t.join()
