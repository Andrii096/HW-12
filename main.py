from collections import UserDict
from datetime import datetime, timedelta
import re
import pickle

class Field:
    def __init__(self, value):
        if not self.is_valid(value):
            raise ValueError("Invalid value")
        self.__value = value

    def __str__(self):
        return str(self.__value)

    def is_valid(self, value):
        return True

    @property
    def value(self):
        return self.__value

    @value.setter
    def value(self, value):
        if not self.is_valid(value):
            raise ValueError("Invalid value")
        self.__value = value

class Name(Field):
    pass

class Phone(Field):

    def __init__(self, value):
        if not self.is_valid(value):
            raise ValueError("Invalid phone number")
        super().__init__(value)

    def is_valid(self, value):
        return value is not None and len(value) == 10 and value.isdigit()

    def __init__(self, value):
        super().__init__(value)

class Birthday(Field):
    def is_valid(self, value):
        try:
            datetime.strptime(value, '%Y-%m-%d')
            return True
        except ValueError:
            return False

    def __init__(self, value=None):
        super().__init__(value)

class Record:
    def __init__(self, name, birthday=None):
        self.name = Name(name)
        self.birthday = Birthday(birthday) if birthday else None
        self.phones = []

    def add_phone(self, phone):
        self.phones.append(Phone(phone))

    def remove_phone(self, phone):
        for p in self.phones:
            if p.value == phone:
                self.phones.remove(p)
                break

    def find_phone(self, phone):
        for p in self.phones:
            if p.value == phone:
                return p
        return None
    
    def __str__(self):
        return f"Contact name: {self.name.value}, phones: {'; '.join(p.value for p in self.phones)}" + (f", birthday: {self.birthday.value}" if self.birthday else "")

    def edit_phone(self, old_phone, new_phone):
        found = False
        for p in self.phones:
            if p.value == old_phone:
                p.value = new_phone
                found = True
                break

            if not found:
                raise ValueError(f"No phone number {old_phone} found to edit.")

    def days_to_birthday(self):
        if not self.birthday:
            raise ValueError("Birthday is not set for this contact.")
        
        now = datetime.now()
        bday = datetime.strptime(self.birthday.value, '%Y-%m-%d').replace(year=now.year)
        
        if bday < now:
            bday = bday.replace(year=now.year + 1)
        
        return (bday - now).days
  
class AddressBook(UserDict):
    def add_record(self, record):
        self.data[record.name.value] = record

    def find(self, name):
        return self.data.get(name, None)

    def delete(self, name):
        if name in self.data:
            del self.data[name]
            
    def __str__(self):
        result = ""
        for record in self.data.values():
            result += str(record) + "\n"
        return result.strip()

    def iterator(self, n):
        records = list(self.data.values())
        for i in range(0, len(records), n):
            yield records[i:i + n]

    def save(self, filename):
        with open(filename, 'wb') as f:
            pickle.dump(self.data, f)

    @classmethod
    def load(cls, filename):
        with open(filename, 'rb') as f:
            data = pickle.load(f)
        address_book = cls()
        address_book.data = data
        return address_book



def input_error(func):
    def inner(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except KeyError:
            return "There's no such name!"
        except ValueError:
            return "Enter valid command!"
        except IndexError:
            return "Give me name and phone please"
    return inner

@input_error
def add_contact(book, name, phone):
    record = Record(name)
    record.add_phone(phone)
    book.add_record(record)
    return f'Contact {name.capitalize()} has been saved!'

@input_error
def change_phone(book, name, phone):
    record = book.find(name)
    if record:
        record.edit_phone(record.phones[0].value, phone)
        return f'Phone number for {name.capitalize()} has been changed!'
    else:
        return f"No contact named {name.capitalize()}."

@input_error
def show_phone(book, name):
    record = book.find(name)
    if record:
        return record.phones[0].value
    else:
        return f"No contact named {name.capitalize()}."

@input_error
def find_contact(book, name):
    record = book.find(name)
    if record:
        return str(record)
    else:
        return f"No contact named {name.capitalize()}."

@input_error
def show_all(book):
    return str(book)

def main():
    filename = 'address_book.pkl'
    try:
        with open(filename, 'rb'):
            book = AddressBook.load(filename)
    except FileNotFoundError:
        book = AddressBook()

    while True:
        command = input("Enter command: ").lower()
        
        if command == "hello":
            print("How can I help you?")
        elif command.startswith("add "):
            _, name, phone = command.split()
            print(add_contact(book, name, phone))
        elif command.startswith("change "):
            _, name, phone = command.split()
            print(change_phone(book, name, phone))
        elif command.startswith("phone "):
            _, name = command.split(maxsplit=1)
            print(show_phone(book, name))
        elif command == "show all":
            print(show_all(book))
        elif command.startswith("find "):
            _, name = command.split(maxsplit=1)
            print(find_contact(book, name))
        elif command in ["good bye", "close", "exit"]:
            book.save(filename)
            print("Good bye!")
            break
        else:
            print("I don't understand this command!")

def main():
    filename = 'address_book.pkl'
    try:
        with open(filename, 'rb'):
            book = AddressBook.load(filename)
    except FileNotFoundError:
        book = AddressBook()

    while True:
        command = input("Enter command: ").lower()
        
        if command == "hello":
            print("How can I help you?")
        elif command.startswith("add "):
            _, name, phone = command.split()
            record = Record(name)
            record.add_phone(phone)
            book.add_record(record)
            print(f'Contact {name.capitalize()} has been saved!')
        elif command.startswith("change "):
            _, name, phone = command.split()
            record = book.find(name)
            if record:
                record.edit_phone(record.phones[0].value, phone)
                print(f'Phone number for {name.capitalize()} has been changed!')
            else:
                print(f"No contact named {name.capitalize()}.")
        elif command.startswith("phone "):
            _, name = command.split(maxsplit=1)
            record = book.find(name)
            if record:
                print(record.phones[0].value)
            else:
                print(f"No contact named {name.capitalize()}.")
        elif command == "show all":
            for record in book.data.values():
                print(record)
        elif command in ["good bye", "close", "exit"]:
            book.save(filename)
            print("Good bye!")
            break
        else:
            print("I don't understand this command!")

if __name__ == "__main__":
    main()
