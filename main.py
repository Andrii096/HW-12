from collections import UserDict
import re
from datetime import datetime, timedelta
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


book = AddressBook()

john_record = Record("John", "1996-01-01")
john_record.add_phone("1234567890")
john_record.add_phone("1111111111")
book.add_record(john_record)

jane_record = Record("Jane")
jane_record.add_phone("0982422277")
book.add_record(jane_record)

# Print all records
for record in book.iterator(1):
    print(record)

# Days to John's next birthday
print(john_record.days_to_birthday())