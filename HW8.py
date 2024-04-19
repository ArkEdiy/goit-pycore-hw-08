import datetime
import pickle
from collections import UserDict

class Field:
    def __init__(self, value):
        self.value = value

    def __str__(self):
        return str(self.value)


class Name(Field):
    def __init__(self, value):
        if value:
            super().__init__(value)
        else:
            raise ValueError("Name cannot be empty")


class Phone(Field):
    def __init__(self, value):
        if len(value) == 10 and value.isdigit():
            super().__init__(value)
        else:
            raise ValueError("Phone number must be a 10-digit number")


class Birthday(Field):
    def __init__(self, value):
        try:
            day, month, year = map(int, value.split('.'))
            self.value = datetime.datetime(year, month, day)
        except ValueError:
            raise ValueError("Invalid date format. Use DD.MM.YYYY")


class Record:
    def __init__(self, name_value):
        self.name = Name(name_value)
        self.phones = []
        self.birthday = None

    def add_phone(self, phone_number):
        self.phones.append(Phone(phone_number))

    def remove_phone(self, phone_number):
        self.phones = [p for p in self.phones if str(p) != phone_number]

    def edit_phone(self, old_phone_number, new_phone_number):
        for i, phone in enumerate(self.phones):
            if str(phone) == old_phone_number:
                self.phones[i] = Phone(new_phone_number)
                return
        raise ValueError("Phone number not found")
    
    def find_phone(self, phone_number):
        for p in self.phones:
            if str(p) == phone_number:
                return p
        return None

    def add_birthday(self, birthday):
        self.birthday = Birthday(birthday)

    def __str__(self):
        phones_str = '; '.join(str(phone) for phone in self.phones)
        if self.birthday:
            return f"Contact name: {self.name.value}, phones: {phones_str}, birthday: {self.birthday.value.strftime('%d.%m.%Y')}"
        else:
            return f"Contact name: {self.name.value}, phones: {phones_str}"


class AddressBook(UserDict):
    def add_record(self, record):
        self.data[record.name.value] = record

    def find(self, name):
        return self.data.get(name)

    def delete(self, name):
        if name in self.data:
            del self.data[name]
        else:
            raise KeyError("Name not found")

    def get_upcoming_birthdays(self):
        upcoming_birthdays = []
        today = datetime.datetime.today()
        next_monday = today + datetime.timedelta((0 - today.weekday()) % 7)
        for record in self.data.values():
            if record.birthday:
                next_birthday = record.birthday.value.replace(year=today.year)
                if next_birthday < today:
                    next_birthday = next_birthday.replace(year=today.year + 1)            
                while next_birthday.weekday() >= 5:
                    next_birthday += datetime.timedelta(days=1)
                days_until_birthday = (next_birthday - today).days
                if days_until_birthday <= 5:
                    upcoming_birthdays.append((record.name.value, next_birthday))
        return [(name, (date + datetime.timedelta((0 - date.weekday()) % 7)).strftime('%d.%m.%Y')) for name, date in upcoming_birthdays]

def input_error(func):
    def handler(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except KeyError:
            return "Enter user name."
        except ValueError:
            return "Give me name and phone please."
        except IndexError:
            return "Provide both name and phone."
        except Exception as e:
            return str(e)

    return handler


def parse_input(user_input):
    cmd, *args = user_input.split()
    cmd = cmd.strip().lower()
    return cmd, *args


@input_error
def add_contact(args, book: AddressBook):
    name, phone, *_  = args
    record = book.find(name)
    message = "Contact updated."
    if record is None:
        record = Record(name)
        book.add_record(record)
        message = "Contact added."
    if phone:
        record.add_phone(phone)
    return message


@input_error
def change_contact(args, book):
    name, old_phone, new_phone = args
    if name in book:
        contact = book[name]
        phone_to_change = contact.find_phone(old_phone)
        if phone_to_change:
            contact.edit_phone(old_phone, new_phone)
            return "Phone number updated for existing contact."
        else:
            return "Old phone number not found for this contact."
    else:
        return "Contact not found."


@input_error
def show_phone(args, book):
    name = args[0]
    if name in book:
        return '\n'.join([f"{phone}" for phone in book[name].phones])
    else:
        return "Contact not found."


@input_error
def show_all(args, book):
    if not book:
        return "No contacts found."
    return '\n'.join([str(record) for record in book.values()])


@input_error
def add_birthday(args, book):
    name, birthday = args
    if name in book:
        book[name].add_birthday(birthday)
        return "Birthday added to existing contact."
    else:
        return "Contact not found."


@input_error
def show_birthday(args, book):
    name = args[0]
    if name in book:
        if book[name].birthday:
            return f"{book[name].birthday.value.strftime('%d.%m.%Y')}"
        else:
            return "No birthday information for this contact."
    else:
        return "Contact not found."


@input_error
def birthdays(args, book):
    upcoming_birthdays = book.get_upcoming_birthdays()
    if not upcoming_birthdays:
        return "No upcoming birthdays in the next week."
    return '\n'.join([f"{record[0]}: {record[1]}" for record in upcoming_birthdays])

def save_data(book, filename="addressbook.pkl"):
    with open(filename, "wb") as f:
        pickle.dump(book, f)

def load_data(filename="addressbook.pkl"):
    try:
        with open(filename, "rb") as f:
            return pickle.load(f)
    except FileNotFoundError:
        return AddressBook()  # Повернення нової адресної книги, якщо файл не знайдено

def main():
    book = load_data()

    print("Welcome to the assistant bot!")
    while True:
        user_input = input("Enter a command: ")
        command, *args = parse_input(user_input)

        if command in ["close", "exit"]:
            save_data(book)
            print("Address book saved. Good bye!")
            break
        elif command == "hello":
            print("How can I help you?")
        elif command == "add":
            print(add_contact(args, book))
        elif command == "change":
            print(change_contact(args, book))
        elif command == "phone":
            print(show_phone(args, book))
        elif command == "all":
            print(show_all(args, book))
        elif command == "add-birthday":
            print(add_birthday(args, book))
        elif command == "show-birthday":
            print(show_birthday(args, book))
        elif command == "birthdays":
            print(birthdays(args, book))
        else:
            print("Invalid command.")

if __name__ == "__main__":
    main()
