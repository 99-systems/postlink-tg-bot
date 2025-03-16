
class SupportProblem:
    def __init__(self, id, name):
        self.id = id
        self.name = name
    
    def __str__(self):
        return self.name.lower()
    
support_problems = [
    SupportProblem(1, 'Не могу дозвониться до Курьера/Отправителя'),
    SupportProblem(2, 'Курьер отказался взять посылку'),
    SupportProblem(3, 'Посылка была утеряна в ходе доставки'),
]

