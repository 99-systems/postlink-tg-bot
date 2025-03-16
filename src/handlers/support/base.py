
class SupportProblem:
    def __init__(self, id, name):
        self.id = id
        self.name = name
    
    def __str__(self):
        return self.name.lower()
    
support_problems = [
    SupportProblem(1, 'Не могу найти курьера/отправителя'),
    SupportProblem(2, 'Вопросы по оплате и доступу к контактам'),
    SupportProblem(3, 'Ошибка в боте/технические проблемы'),
    SupportProblem(4, 'Вопросы по правилам, безопасности и условиям сервиса'),
    SupportProblem(5, 'Курьер отказался взять посылку'),
    SupportProblem(6, 'Посылка была утеряна в ходе доставки'),
    SupportProblem(7, 'Не могу зарегистрироваться'),
    SupportProblem(8, 'Другая проблема')
]

