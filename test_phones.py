from onlinesimru import GetFree, GetRent, GetProxy, GetUser, GetNumbers

TOKEN = 'f3e2bf5ca5465cf96f10aee0ed535ff4'


def main():
    numbers = GetNumbers(TOKEN)

    # tariffs = numbers.tariffsOne(country=7)
    number = numbers.get(service='yandex', number=True)
    print(numbers.stateOne(tzid=number['tzid'], message_to_code=1, msg_list=0))



main()
