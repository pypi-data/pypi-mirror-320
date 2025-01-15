'''A small and useful for support some everyday requirements in python
یک کتابخانه ی کوچک و کاربردی برای رفع برخی نیاز های روزمره در پایتون'''

class mtr(str):
    '''A helper class for strings that can have extra features.
    یک کلاس کمکی برای رشته ها در پایتون با برخی قابلیت های اضافی.'''
    def __init__(self, text):
        # super().__init__(self)
        self.text = text

    def insert_text(self, new_text:str, index:int, replace:bool=False, inplace:bool=True):
        '''اضافه کردن یک زیررشته درون یک رشته
        :param new_text: The substring that should insert in string - زیررشته ای که باید درون رشته قرار بگیرد
        :param index: اندیسی که باید زیررشته قرار بگیره
        :param inplace: مشخص کننده ی اینکه نتیجه ی بدست آمده در متغیر جدید ذخیره شود یا برابر با رشته ی قبلی شود
        '''
        if replace:
            # جایگزین کردن متن در ایندکس
            self.text = self.text[:index] + new_text + self.text[index + len(new_text):]
        elif inplace:
            # اضافه کردن متن در ایندکس (بدون جایگزینی)
            self.text = self.text[:index] + new_text + self.text[index:]
        else:
            # ایجاد رشته جدید
            if replace:
                return self.text[:index] + new_text + self.text[index + len(new_text):]
            return self.text[:index] + new_text + self.text[index:]

    def __str__(self):
        return self.text

def iinput(prompt:str) -> int:
    '''Read a int'''
    print(prompt, end='')
    return int(input())

