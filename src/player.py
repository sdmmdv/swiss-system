class Player:
    def __init__(self, rank, id, name, is_bye):
        self.rank = rank
        self.id = id
        self.name = name
        self.is_bye = is_bye

    def __str__(self):
        return f'{self.id} {self.name}'
    
    def print_main(self):
        print(f'ID: {self.id}, Rank: {self.rank}, Name: {self.name}, Bye: {self.is_bye}')