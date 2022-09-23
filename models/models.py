from mongoengine import *
from datetime import date

connect(host='mongodb://localhost:27017/assistant')


class Contacts(Document):
    name = StringField(max_length=30, unique=True, required=True)
    address = StringField(max_length=100)
    birthday = DateField()
    phones = ListField(StringField(max_length=15, unique=True))
    emails = ListField(StringField(max_length=254, unique=True))

    def days_to_birthday(self) -> int:
        if self.birthday is None:
            return -1
        this_day = date.today()
        birthday_day = date(this_day.year, self.birthday.month, self.birthday.day)
        if birthday_day < this_day:
            birthday_day = date(this_day.year + 1, self.birthday.month, self.birthday.day)
        return int((birthday_day - this_day).days)



class Notes(Document):
    _id = SequenceField(required=True)
    text = StringField(min_length=1, max_length=255, required=True)
    tags = ListField(StringField(min_length=1, max_length=15, required=True))
    execution_date = DateField()
    is_done = BooleanField(default=False)
