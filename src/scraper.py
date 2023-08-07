from ScrapeThread import ScrapeThread

url: str = "https://www.google.com/travel/flights?tfs=CBwQARoaEgoyMDIzLTEwLTA4agwIAhIIL20vMGZ0anhAAUgBcAGCAQsI____________AZgBAg&hl=en-GB&curr=EUR"

destinations = [
    ("Sofia", "Eindhoven", "23 Aug"), 
    ("Canada", "Rome", "23 Aug"),
    ("Canada", "Rome", "2 Sep")
]

cities = [
    "Sofia",
    "Eindhoven",
    "Paris",
    "Rome",
    "Lisbon",
    "Bucharest",
    "Budapest"
]

wanted_date = "26 Aug"

destinations = [("Sofia", "Eindhoven", "{} Aug".format(i)) for i in range(8, 32)]

WORKERS = 4

delegated_work = [[] for i in range(WORKERS)]

if __name__ == '__main__':
    k = 0
    for c1, c2, d in destinations:
        delegated_work[k].append((c1, c2, d))
        k += 1
        k %= WORKERS
    #for city_1 in cities:
    #    for city_2 in cities:
    #        if city_1 != city_2:
    #            delegated_work[k].append((city_1, city_2, wanted_date))
    #            k += 1
    #            k %= WORKERS

    all_threads = []
    for x in delegated_work:
        t = ScrapeThread(url, x)
        t.start()

        all_threads.append(t)
    for t in all_threads:
        t.join()
