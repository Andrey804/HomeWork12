import sys, re, pickle
from datetime import datetime
from collections import UserDict


class UserNameError(Exception):
    pass


class UserNumberError(Exception):
    pass


class UserChangingNumberError(Exception):
    pass


class UserNewNumberError(Exception):
    pass


class UserBirthdayError(Exception):
    pass


class UserSearchError(Exception):
    pass


class CustomIterator:
    def __init__(self, value, n):
        self.dicts = value
        self.n = n
        self.key = []
        for i in value:
            self.key.append(i)

    def __iter__(self):
        return self

    def __next__(self):
        if len(self.key):
            self.iter_dicts = {}
            for i in range(self.n):
                if len(self.key):
                    self.iter_dicts.update([(self.key[0], self.dicts.pop(self.key[0]))])
                    del self.key[0]
                else:
                    break

            return self.iter_dicts
        raise StopIteration


class AddressBook(UserDict):

    def add_record(self, record):
        self.data[record.name.value] = record
        return f"Contact with name: '{record.name.value}'" + \
               (f", and phone number: '{record.phones[-1].value}'" if record.is_entered_phone is not False else "") + \
               f" - has been successfully added!"

    def phone_user(self, name_or_phone):
        for name, contact in self.data.items():
            if name_or_phone == name:

                birthday_show = ". Birthday is not listed!"
                if contact.birthday.value:
                    user_birthday = contact.birthday.value
                    days_to_birthday = contact.days_to_birthday()
                    birthday_show = f". Birthday in {user_birthday}, {days_to_birthday} days left!" if days_to_birthday != 0 else ". Birthday is today!"

                return f"{name} -> " + \
                       ', '.join([phone.value for phone in contact.phones] if len(contact.phones) > 0 else
                                 ['(No phone numbers)']) + birthday_show

            for contact_phone in contact.phones:
                if name_or_phone == contact_phone.value:

                    birthday_show = ". Birthday is not listed!"
                    if contact.birthday.value:
                        user_birthday = contact.birthday.value.strftime('%d.%m.%Y')
                        days_to_birthday = contact.days_to_birthday()
                        birthday_show = f". Birthday in {user_birthday}, {days_to_birthday} days left!" if days_to_birthday != 0 else ". Birthday is today!"

                    return f"{name} -> " + \
                           ', '.join([phone.value for phone in contact.phones] if len(contact.phones) > 0 else
                                     ['(No phone numbers)']) + birthday_show

        return f"Contacts with this name or phone: {name_or_phone} - not found!"

    def search(self, n, name_or_phone):
        res = {}
        for name, contact in self.data.items():
            if re.search(name_or_phone, name, flags=re.IGNORECASE):
                res[name] = contact

            for contact_phone in contact.phones:
                if re.search(name_or_phone, contact_phone.value, flags=re.IGNORECASE):
                    res[name] = contact

        if res:
            return self.iterator(n, res)
        else:
            return "Contacts with this data: {name_or_phone} - not found!"

    def show_all(self):

        if not bool(self.data):
            return "Address book is empty!"

        longest_name = max([len(names) for names in self.data])

        return "\n".join([f"{str(contact.name.value):<{longest_name}} -> " +
                          (", ".join([i.value for i in contact.phones] if len(contact.phones) > 0
                                     else ['(No phone numbers)']))
                          for contact in self.data.values()])

    def iterator(self, n=10, some_dict=None):

        if not bool(self.data):
            return "Address book is empty!"

        if some_dict is None:
            return CustomIterator(self.data.copy(), n)
        else:
            return CustomIterator(some_dict.copy(), n)


class Record:
    def __init__(self, name):
        self.name = Name(name)
        self.birthday = Birthday()
        self.is_entered_phone = False

        self.phones = []
        user_contacts_values = address_book.data.get(self.name.value)
        if user_contacts_values is not None:
            self.phones = user_contacts_values.phones

    def add_new_phone(self, phone):
        if phone:

            for contact in address_book.values():
                for contact_phone in contact.phones:
                    if phone == contact_phone.value:
                        return f"In a contact with the name: '{contact.name.value}', the phone number: '{phone}'" \
                               f" - has been already exists!"

            self.is_entered_phone = True
            user_phone = Phone()
            user_phone.variable = phone
            self.phones.append(user_phone)

        else:
            if self.name.value in address_book:
                return f"Contact with name: '{self.name.value}' - has been already created!"

    def change_phone(self, phone, new_phone):
        for phones in self.phones:
            if phones.value == phone:
                id_remove_phone = self.phones.index(phones)
                self.phones.remove(phones)
                self.phones.insert(id_remove_phone, Phone(new_phone))
                return f"In the contact with the name: '{self.name.value}'" \
                       f" - the phone number: '{phone}' was successfully changed to '{new_phone}'!"
        return f"In contact with name: '{self.name.value}', phone number: '{phone}' - not found!"

    def remove_phone(self, phone):
        for phones in self.phones:
            if phones.value == phone:
                self.phones.remove(phones)
                return f"In the contact with name: '{self.name.value}'" \
                       f" - phone: '{phone}' has been successfully removed!"
        return f"In contact with name: '{self.name.value}', phone number: '{phone}' - not found!"

    def add_birthday(self, birthday):
        self.birthday.variable = birthday
        return f"Contact with the name: {self.name.value} - successfully added a birthday: {birthday}!"

    def days_to_birthday(self):
        if self.birthday.value:
            date_now = datetime.now().date()
            date_user = datetime.strptime(self.birthday.value, "%d.%m.%Y").date()
            next_birthday = date_user.replace(year=date_now.year)

            if date_user.month <= date_now.month and date_user.day < date_now.day:
                next_birthday = next_birthday.replace(year=date_now.year + 1)

            return (next_birthday - date_now).days


class Field:
    def __init__(self, value=None):
        self.value = value


class Name(Field):
    pass


class Phone(Field):
    @property
    def variable(self):
        return self.value

    @variable.setter
    def variable(self, var):
        if re.fullmatch(r"\+?\d{12}", var) is None:
            self.value = ""
        else:
            self.value = var


class Birthday(Field):
    @property
    def variable(self):
        return self.value

    @variable.setter
    def variable(self, var):
        if re.match(r"\d\d\.\d\d\.\d{4}", var) is None:
            self.value = None
        else:
            self.value = var


# основна функція, яка працює з користувачем, приймає та виводить інформацію
def main():
    entered_str = None

    with open('Address_book.bin', 'rb') as file:
        unpacked = pickle.load(file)
        address_book.update(unpacked)

    while True:
        entered_str = input("\n-- To see existing commands, type <help> or <info> --\n\n"
                            "Hello!\n>>>") if entered_str is None else input(">>>")
        key = None

        for i in dict_of_keys.keys():
            if re.match(i, entered_str.lower()):
                key = i
                entered_str = entered_str.lower().removeprefix(key).removeprefix(" ").capitalize()
                break

        if key is None:
            print("I don't understand what you want from me!\n"
                  "(An invalid command was entered. To see existing commands, type <help> or <info>)")
            continue

        print(handler(key, entered_str))

        if key == "add" or key == "change" or key == "remove" or key == "delete" or key == "birthday":
            with open('Address_book.bin', 'wb') as file:
                pickle.dump(address_book, file)


# функція-декоратор, яка перевіряє строку, введену користувачем, на винятки
def input_error(func):
    def wrappers(key, entered_str):
        try:
            return func(key, entered_str)

        except KeyError:
            return "I don't understand what you want from me!\n" \
                   "(An invalid command was entered. To see existing commands, type <help> or <info>)"

        except UserNameError:
            return "You entered the invalid name!\n" \
                   "(The name must begin with a Latin letter, have no spaces, " \
                   "and be separated from the command by one space)"

        except UserNumberError:
            return "You entered the invalid number!\n" \
                   "(The phone number should look like this: 380888888888, and be separated from the name by one space)"

        except UserChangingNumberError:
            return "You entered the invalid changing number!\n" \
                   "(The phone number should look like this: 380888888888, and be separated from the name by one space)"

        except UserNewNumberError:
            return "You entered the invalid new number!\n" \
                   "(The phone number should look like this: 380888888888, " \
                   "and be separated from the changing number by one space)"

        except UserBirthdayError:
            return "You entered the invalid birthday!\n" \
                   "(The birthday should look like this: dd.mm.yyyy, and be separated from the name by one space)"

        except UserSearchError:
            return "You entered an invalid search query!\n" \
                   "(A search query should consist of either only letters to search by name " \
                   "or only numbers to search by phone number. No spaces)"
    return wrappers


# функція, яка працює з введеною користувачем строкою
@input_error
def handler(key, entered_str):

    if key == "phone":
        if not entered_str:
            raise UserNameError()
        if re.match(r"[a-zA-Z]\w+|\+?\d{12}", entered_str) is None:
            raise UserNameError()
        name_or_phone, other = re.split(" ", entered_str + " ", maxsplit=1)
        return dict_of_keys[key](name_or_phone)

    if key == "search":
        if not entered_str:
            raise UserNameError()
        if re.fullmatch(r"[a-zA-Z]+|\+?\d+", entered_str) is None:
            raise UserSearchError()
        name_or_phone, other = re.split(" ", entered_str + " ", maxsplit=1)
        return dict_of_keys[key](name_or_phone)

    name, data = re.split(" ", entered_str + "  ", maxsplit=1)

    if key == "add" or key == "remove":
        if not entered_str:
            raise UserNameError()
        if re.match(r"\+?\d{12}| *$", data) is None:
            raise UserNumberError()
        phone, other = re.split(" ", data, maxsplit=1)
        phone = phone.removeprefix("+")
        return dict_of_keys[key](name, phone)

    elif key == "change":
        if not entered_str:
            raise UserNameError()
        if re.match(r"\+?\d{12}", data) is None:
            raise UserChangingNumberError()
        if re.match(r"\+?\d{12} \+?\d{12}", data) is None:
            raise UserNewNumberError()
        phone, new_phone, other = re.split(" ", data, maxsplit=2)
        phone = phone.removeprefix("+")
        new_phone = new_phone.removeprefix("+")
        return dict_of_keys[key](name, phone, new_phone)

    elif key == "delete":
        if not entered_str:
            raise UserNameError()
        return dict_of_keys[key](name)

    elif key == "birthday":
        if not entered_str:
            raise UserNameError()
        if re.match(r"\d\d\.\d\d\.\d{4}", data) is None:
            raise UserBirthdayError()
        birthday, other = re.split(" ", data, maxsplit=1)
        return dict_of_keys[key](name, birthday)

    return dict_of_keys[key]()


# бот виводить у консоль привітання
def hello(*args, **kwargs):
    return "How can I help you?"


# бот зберігає в пам'яті новий контакт або додає номер до існуючого
def add(name, phone):
    record = Record(name)
    is_skipping_add = record.add_new_phone(phone)
    if bool(is_skipping_add):
        return is_skipping_add
    return address_book.add_record(record)


def add_birthday(name, birthday):
    if name in address_book:
        return address_book[name].add_birthday(str(birthday))
    else:
        return f"Contact name: '{name}' - not found!"


# бот змінює номер існуючого контакту
def change(name, phone, new_phone):
    if name in address_book:
        return address_book[name].change_phone(phone, new_phone)
    else:
        return f"Contact name: '{name}' - not found!"


# бот змінює номер існуючого контакту
def remove_phone(name, phone):
    if name in address_book:
        return address_book[name].remove_phone(phone)
    else:
        return f"Contact name: '{name}' - not found!"


# бот видаляє існуючий контакт
def delete_user(name):
    if name in address_book:
        del address_book[name]
        return f"Contact with name: '{name}' - has been successfully deleted!"
    else:
        return f"Contact name: '{name}' - not found!"


# бот виводить у консоль номер телефону для зазначеного контакту
def phone_user(name_or_phone):  # phone and
    return address_book.phone_user(name_or_phone)


def search(data):
    num_lines_in_page = 10
    res = []
    num_page = 0

    for i in address_book.search(num_lines_in_page, data):
        num_page += 1
        longest_name = max([len(names) for names in i])
        write_num_page = f"page {str(num_page)}"

        page = ("\n".join([f"{str(contact.name.value):<{longest_name}} -> " +
                           (", ".join([i.value for i in contact.phones] if len(contact.phones) > 0
                                      else ['(No phone numbers)']))
                           for contact in i.values()]))

        res.append(page + f"\n{write_num_page:_^{longest_name * 2 + 4}}")

    return "\n\n".join(res)


# бот виводить у консоль список всіх контактів
def show_all(*args, **kwargs):
    num_lines_in_page = 10
    res = []
    num_page = 0

    for i in address_book.iterator(num_lines_in_page):
        num_page += 1
        longest_name = max([len(names) for names in i])
        write_num_page = f"page {str(num_page)}"

        page = ("\n".join([f"{str(contact.name.value):<{longest_name}} -> " +
                        (", ".join([i.value for i in contact.phones] if len(contact.phones) > 0
                                   else ['(No phone numbers)']))
                        for contact in i.values()]))

        res.append(page + f"\n{write_num_page:_^{longest_name * 2 + 4}}")

    return "\n\n".join(res)


# бот виводить у консоль список всіх команд
def info(*args, **kwargs):
    longest_keys = 0
    for i in dict_of_description.keys():
        if len(i) > longest_keys:
            longest_keys = len(i)
    return "All existing keys:\n\n" \
           "!!! WARNING: THERE SHOULD BE ONLY ONE SPACE BETWEEN ALL WORDS " \
           "AND THE NAME MUST CONTAIN ONLY LATIN LETTERS !!!\n\n" + \
           "\n".join([f"{f'<{key}>':<{longest_keys + 2}} -> " +
                      f"\n{r'    ':_>{longest_keys + 6}}".join(desc)
                      for key, desc in dict_of_description.items()])


# бот віходить із програми
def close(*args, **kwargs):
    sys.exit("Good bye!")


# словник з усіма командами
dict_of_keys = {
    "hello": hello,
    "hi": hello,
    "add": add,
    "birthday": add_birthday,
    "change": change,
    "remove": remove_phone,
    "delete": delete_user,
    "phone": phone_user,
    "search": search,
    "show all": show_all,
    "info": info,
    "help": info,
    "good bye": close,
    "close": close,
    "exit": close,
    "no": close
}

# словник з описом усіх команд
dict_of_description = {
    "hello": ["Greetings command", "(Need only one command)"],
    "hi": ["Greetings command", "(Need only one command)"],
    "add": ["Command to add a new contact or another number to an existing one",
            "(After the command, write the name of the new contact, and then the phone number of the "
            "form '380888888888'. If you do not add a phone number, the contact will only be created with the "
            "name you specified. If a contact with this name exists, the specified number will be added to it)"],
    "birthday": ["Command to add a birthday to an existing contact",
                 "(After the command, write the name of the existing contact, then the birthdate you want to add "
                 "the form 'dd.mm.yyyyy'. The existing birthdate is replaced with the new one)"],
    "change": ["Command to change the number of an existing contact",
               "(After the command, write the name of the existing contact, then the number you want to change "
               "and then the phone number in the form '380888888888')"],
    "remove": ["Command to remove the number of an existing contact",
               "(After the command, write the name of the existing contact and then the phone number in the "
               "form '380888888888' that you want to remove)"],
    "delete": ["Command to delete an existing contact",
               "(After the command, write the name of the contact you want to delete)"],
    "phone": ["Command to display information about an existing contact",
              "(After the command, write the name of the existing contact whose information you want to know)"],
    "show all": ["Command to display all contacts", "(Need only one command)"],
    "info": ["A helper command that shows all possible commands and their descriptions", "(Need only one command)"],
    "help": ["A helper command that shows all possible commands and their descriptions", "(Need only one command)"],
    "good bye": ["Program exit command", "(Need only one command)"],
    "close": ["Program exit command", "(Need only one command)"],
    "exit": ["Program exit command", "(Need only one command)"],
    "no": ["Program exit command", "(Need only one command)"]
}

# запуск програми
if __name__ == "__main__":
    address_book = AddressBook()
    # handler('add', "Andrey 380818888888")
    # handler('add', "Mary 380717777777")
    # handler('add', "Mary 380727777777")
    # handler('add', "Sasha 380616666666")
    # handler('add', "Ivan")
    # handler('add', "Maksim 380515555555")
    # handler('add', "Oleg 380919999999")
    # handler('add', "Siusan 380414444444")
    # handler('add', "Siusan 380424444444")
    # handler('add', "Katya 380313333333")
    # handler('add', "Peter")
    # handler('add', "Bob 380212222222")
    # handler('add', "Vasya 380111111111")
    # handler('add', "Alexander 380010000000")
    # handler('birthday', "Mary 23.03.1998")
    # handler('birthday', "Bob 20.08.1985")
    # print(handler('show all', ""))
    # print('\n>>>phone Mary')
    # print(handler('phone', "Mary"))

    main()
    # runfile(D:/Python_project/GoIT/module/Lesson11/HW11/main.py)
