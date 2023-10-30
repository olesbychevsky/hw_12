from collections import UserDict
from datetime import datetime
import pickle
import re


class Field:
    def __init__(self, name):
        self.value = name


class AddressBook(UserDict):

    file_to_save = "Contacts.txt"

    def save_to_file(self):
        with open(self.file_to_save, "wb") as file:
            pickle.dump(self, file)

    def read_from_file(self):
        with open(self.file_to_save, "rb") as file:
            self.data = pickle.load(file)
        return self

    def search(self, user_input):
        matched = []
        match = re.findall("\w+", user_input)
        match_birthday = re.findall("\d{2}.\d{2}.\d{4}", user_input)
        if match.isalpha():
            for i in self.data.values:
                if match in i.name.value:
                    matched.append(i)
        
        elif match.isdigit():
            for i in self.data.values:
                for j in i.phone:
                    if match in j.value:
                        matched.append(i)
        
        elif match_birthday:
            for i in self.data.values:
                for j in i.birthday:
                    if match_birthday in j.value:
                        matched.append(i)

        else:
            print(f'Can contain only letters, numbers or numbers or dots.')
        
        return matched

    def add_record(self, record):
        self.data[record.name.value] = record

    def find(self, name):
        return self.data.get(name)

    def delete(self, name):
        if name in self.data:
            del self.data[name]

    def __iter__(self, records_per_page=10):
        self.records_per_page = records_per_page
        self.current_page = 1
        self.current_index = 0
        return self

    def __next__(self):
        if self.current_index >= len(self.data):
            raise StopIteration
        records = list(self.data.values())[
            self.current_index:self.current_index + self.records_per_page]
        self.current_index += self.records_per_page
        self.current_page += 1
        return records


class Name(Field):
    pass


class Phone(Field):
    def __init__(self, number):
        if not self.is_valid_phone(number):
            raise ValueError('Phone number must be a 10-digit number.')
        super().__init__(number)

    @staticmethod
    def is_valid_phone(number):
        return len(number) == 10 and number.isdigit()


class Birthday(Field):
    def __init__(self, date):
        self.validate_birthday(date)
        super().__init__(date)

    @staticmethod
    def validate_birthday(date):
        try:
            datetime.strptime(date, '%Y-%m-%d')
        except ValueError:
            raise ValueError("Invalid birthday format. Use YYYY-MM-DD.")


class Record:
    def __init__(self, name, birthday=None):
        self.name = Name(name)
        self.phones = []
        self._birthday = None
        self.birthday = birthday

    def add_phone(self, phone):
        if self.is_valid_phone(phone):
            self.phones.append(Phone(phone))
        else:
            raise ValueError('Phone number must be a 10-digit number.')

    @staticmethod
    def is_valid_phone(number):
        return len(number) == 10 and number.isdigit()

    def edit_phone(self, old_phone, new_phone):
        phone_to_edit = self.find_phone(old_phone)
        if phone_to_edit:
            phone_to_edit.value = new_phone
            return f'Phone {old_phone} has been updated to {new_phone} in the record: {self.name.value}'
        else:
            raise ValueError()

    def find_phone(self, phone_to_find):
        for phone in self.phones:
            if phone.value == phone_to_find:
                return phone
        return None

    def remove_phone(self, phone):
        for p in self.phones:
            if p.value == phone:
                return self.phones.remove(p)

    @property
    def birthday(self):
        return self._birthday

    @birthday.setter
    def birthday(self, value):
        if value:
            self.validate_birthday(value)
        self._birthday = value

    @staticmethod
    def validate_birthday(date):
        try:
            datetime.strptime(date, '%Y-%m-%d')
        except ValueError:
            raise ValueError("Invalid birthday format. Use YYYY-MM-DD.")


def input_error(func):
    def inner(user_string):
        try:
            result = func(user_string)
            return result
        except KeyError:
            return 'Enter user name:'
        except ValueError as e:
            return str(e)
        except IndexError:
            return 'Please enter command, name, and phone (and optionally birthday).'
    return inner


COMMANDS_DESCRIPTION = {
    'add': 'Add a new contact',
    'add_phone': 'Add a new phone to an existing contact',
    'change': 'Change a contact\'s phone number',
    'phone': 'Get the phone number for a contact',
    'hello': 'Greet the bot',
    'show_all': 'Show all contacts',
    'good bye': 'Exit the bot',
    'close': 'Exit the bot',
    'exit': 'Exit the bot',
    'help': 'Show available commands',
}


def create_data(data):
    if len(data) < 2 or len(data) > 3:
        raise IndexError(
            'Please enter command, name, and phone (and optionally birthday).')
    name = Name(data[0])
    phone = Phone(data[1])
    birthday = data[2] if len(data) > 2 else None
    return name, phone, birthday


@input_error
def add_contact(data):
    name, phone, birthday = create_data(data)
    record_add = Record(name, birthday)
    if record_add.is_valid_phone(phone.value):
        record_add.add_phone(phone.value)
        addressbook.add_record(record_add)
        if birthday:
            return f'A new contact added successfully. Name: {name.value}, Phone: {phone.value}, Birthday: {birthday}'
        else:
            return f'A new contact added successfully. Name: {name.value}, Phone: {phone.value}'
    else:
        return 'Phone number must be a 10-digit number.'


@input_error
def add_new_phone(data):
    if len(data) != 2:
        return 'Please enter a contact name and a phone number.'
    name = Name(data[0])
    phone = Phone(data[1])
    record_add_phone = addressbook.data.get(name.value)
    if record_add_phone:
        record_add_phone.add_phone(phone)
        return f'A new phone: {phone.value}, has been added to contact name: {name.value}.'
    else:
        return f'Contact with name "{name.value}" not found in the address book.'


@input_error
def change_contact(data):
    name, phone = create_data(data)
    new_phone = Phone(data[2])

    record_change = addressbook.data.get(name.value)
    if record_change:
        try:
            return record_change.edit_phone(phone.value, new_phone.value)
        except ValueError as e:
            return str(e)
    else:
        return f'Contact with name "{name.value}" not found in the address book.'


@input_error
def get_number(name_contact):
    name = name_contact[0]
    record = addressbook.data.get(name.value)
    if record:
        phones = ', '.join([phone.value for phone in record.phones])
        return f"Name: {name.value}, Phones: {phones}"
    else:
        return f'Contact with name "{name.value}" not found in the address book.'


@input_error
def show_all_func(show_all_command):
    result = 'All contacts:\n'
    for name, record in addressbook.data.items():
        phones = ', '.join([phone.value for phone in record.phones])
        result += f"Name: {record.name.value}, Phone: {phones}\n"
    return result


@input_error
def quit_func(quit_command):
    return 'Thank you for using our BOT!'


@input_error
def hello_func(hello_command):
    return "Hello! How can I help you?"


@input_error
def help_func(help_command):
    commands_list = "\n".join(
        [f"{cmd}: {description}" for cmd, description in COMMANDS_DESCRIPTION.items()])
    return f"Available commands:\n{commands_list}"


@input_error
def find_contact(data):
    name = data[0]
    return addressbook.find(name)


@input_error
def delete_contact(data):
    name = data[0]
    if name.value in addressbook.data:
        del addressbook.data[name.value]
        return f'Contact with name "{name.value}" has been deleted.'
    else:
        return f'Contact with name "{name.value}" not found in the address book.'


def main():
    global addressbook
    addressbook = AddressBook()

    COMMANDS = {
        'add': add_contact,
        'add_phone': add_new_phone,
        'change': change_contact,
        'phone': get_number,
        'hello': hello_func,
        'show_all': show_all_func,
        'good bye': quit_func,
        'close': quit_func,
        'exit': quit_func,
        'help': help_func,
        'delete': delete_contact,
        'find': find_contact,
    }

    print('Welcome to BOT >>>')

    while True:
        user_input = input('Enter a command: ').strip().lower()

        if user_input == '.':
            break

        input_parts = user_input.split()
        if input_parts:
            command = input_parts[0]
            arguments = input_parts[1:]

            if command in COMMANDS:
                result = COMMANDS[command](arguments)
                if result:
                    print(result)
            else:
                print(f"Invalid command: {command}")


if __name__ == "__main__":
    main()
