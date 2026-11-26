from .graph import HubData
from .parsing import ParsingData, ParsingValidator, ValidatorParserConnection,ValidatorParserDrone,ValidatorParserHub
import pygame

#class Visualisation:
#    def __init__(self):
#        self.name = "test"
#        self.pos_x = 0
#        self.pos_y = 0
#        self.link = ""

#    def resize_all(self):



if __name__ == "__main__":
    try:
        test = ParsingValidator()
        valid_drone = ValidatorParserDrone
        valid_hub = ValidatorParserHub
        valid_connection = ValidatorParserConnection
        data = test.read_file("config.txt")
        test2 = ParsingData()
        test.check_data(data, valid_drone, valid_hub, valid_connection)
        value = test2.pick_data(data)
    except BaseException as error:
        print(error)

    #ger = []
    #for i, j in value['hubs'].items():
    #    k = HubData(i, j)
    #    ger.append(k)
    #print([ger[i].pos_x for i in range(len(ger))])
    pygame.init()

    screen = pygame.display.set_mode((800, 600))
    pygame.display.set_caption("Fly-in 42")

    running = True
    background = pygame.image.load("src/asset/back.jpg")
    background = pygame.transform.scale(background, (800, 600))

    plateform = pygame.image.load("src/asset/test.jpeg")
    plateform = pygame.transform.scale(plateform, (50,50))

    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        screen.blit(background, (0,0))
        for i, j in value['hubs'].items():
            k = HubData(i, j)
            screen.blit(plateform, (k.pos_x, k.pos_y))
        pygame.display.flip()
    pygame.quit()

