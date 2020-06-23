import pygame
import sys
import time
from pygame.locals import *
from random import randint

"""坦克大战的主窗口"""


class TankMain(object):
    width = 600
    height = 500
    my_tank = None  # 创建一个我方坦克
    # enemy_list = []
    wall = None
    enemy_list = pygame.sprite.Group()  # 得到一个敌方坦克的组
    my_tank_missile_list = []
    explode_list = []  # 创建一个爆炸列表
    enemy_missile_list = pygame.sprite.Group()  # 得到一个敌方炮弹的组

    # 开始游戏的方法
    def startGame(self):
        pygame.init()  # pygame模块初始化，加载系统资源

        # 创建一个屏幕，屏幕（窗口）的大小（宽，高），窗口的特性(0,RESIZABLE,FULLSCREEN)
        screen = pygame.display.set_mode((TankMain.width, TankMain.height), 0, 32)

        # 给窗口设置一个标题
        pygame.display.set_caption("坦克大战")

        # 创建一堵墙
        TankMain.wall = Wall(screen, 80, 160, 20, 200)
        TankMain.my_tank = My_Tank(screen)  # 创建一个我方坦克

        if len(TankMain.enemy_list) == 0:
            for i in range(1, 6):  # 游戏开始时候初始化5个敌方坦克
                TankMain.enemy_list.add(Enemy_Tank(screen))  # 把敌方坦克放到组里面

        while True:
            if len(TankMain.enemy_list) < 5:
                TankMain.enemy_list.add(Enemy_Tank(screen))
            # color RGB(0,0,0),(255,255,255),设置屏幕的背景色为黑色：
            screen.fill((0, 0, 0))

            # 显示左上角的文字
            for i, text in enumerate(self.write_text(), 0):
                screen.blit(text, (0, 5 + (16 * i)))

            # 显示游戏中的墙，并对墙和其他对象进行碰撞检测
            TankMain.wall.display()
            TankMain.wall.hit_other()

            self.get_event(TankMain.my_tank, screen)  # 获取事件，根据获取到的事件进行处理
            if TankMain.my_tank:
                TankMain.my_tank.hit_enemy_missile()  # 我方的坦克和敌方的炮弹进行碰撞检测

            if TankMain.my_tank and TankMain.my_tank.live:
                TankMain.my_tank.display()  # 在屏幕上显示我放坦克
                TankMain.my_tank.move()  # 在屏幕上移动我方坦克
            else:
                TankMain.my_tank = None

            # 显示和随机显示敌方坦克
            for enemy in TankMain.enemy_list:
                enemy.display()
                enemy.random_move()
                enemy.random_fire()

            # 显示所有的我方炮弹
            for m in TankMain.my_tank_missile_list:
                if m.live:
                    m.display()
                    m.hit_tank()  # 炮弹打中了敌方坦克
                    m.move()
                else:
                    TankMain.my_tank_missile_list.remove(m)

            # 显示所有的敌方炮弹
            for m in TankMain.enemy_missile_list:
                if m.live:
                    m.display()
                    m.move()
                else:
                    TankMain.enemy_missile_list.remove(m)

            #
            for explode in TankMain.explode_list:
                explode.display()

            time.sleep(0.05)  # 睡眠0.05秒之后再重置
            # 显示重置
            pygame.display.update()

    # 获取所有的事件（敲击键盘、鼠标点击等）
    def get_event(self, my_tank, screen):
        for event in pygame.event.get():
            if event.type == QUIT:
                self.stopGame()  # 程序退出
            if event.type == KEYDOWN and (not my_tank) and event.key == K_r:
                TankMain.my_tank = My_Tank(screen)
            if event.type == KEYDOWN and my_tank:
                if event.key == K_RIGHT:
                    my_tank.direction = "R"
                    my_tank.stop = False
                    # my_tank.move()
                if event.key == K_LEFT:
                    my_tank.direction = "L"
                    my_tank.stop = False
                    # my_tank.move()
                if event.key == K_UP:
                    my_tank.direction = "U"
                    my_tank.stop = False
                    # my_tank.move()
                if event.key == K_DOWN:
                    my_tank.direction = "D"
                    my_tank.stop = False
                    # my_tank.move()
                if event.key == K_ESCAPE:
                    self.stopGame()
                if event.key == K_SPACE:
                    m = my_tank.fire()
                    m.good = True  # 我方坦克发射的炮弹，好炮弹
                    TankMain.my_tank_missile_list.append(m)
            if event.type == KEYUP and my_tank:
                if event.key == K_LEFT or event.key == K_RIGHT or event.key == K_UP or event.key == K_DOWN:
                    my_tank.stop = True

    # 关闭游戏
    def stopGame(self):
        sys.exit()

    # 在屏幕左上角显示文字内容
    def write_text(self):
        font = pygame.font.SysFont("华文仿宋", 16)  # 定义一个字体
        text_sf1 = font.render("敌方坦克数量为：%d" % len(TankMain.enemy_list), True, (255, 150, 0))  # 根据字体创建一个文件的图像
        text_sf2 = font.render("我方坦克炮弹数量为：%d" % len(TankMain.my_tank_missile_list), True, (255, 150, 0))
        return text_sf1, text_sf2


# 坦克大战游戏中所有对象的父类
class BaseItem(pygame.sprite.Sprite):

    def __init__(self, screen):
        pygame.sprite.Sprite.__init__(self)
        # 所有对象公共的属性
        self.screen = screen  # 坦克在移动或者显示过程中需要用到的当前游戏的屏幕

    # 把坦克对应的图片显示在游戏窗口中
    def display(self):
        if self.live:
            self.image = self.images[self.direction]
            self.screen.blit(self.image, self.rect)


# 坦克的公共父类
class Tank(BaseItem):
    # 定义类属性，所有坦克对象高和宽都是一样
    width = 50
    height = 50

    def __init__(self, screen, left, top):
        super().__init__(screen)
        self.direction = "D"  # 坦克的方向，默认方向往下
        self.speed = 5  # 坦克移动的速度
        self.stop = False  # 坦克停止的初始值为false
        self.images = {}  # 坦克的所有图片，key：方向，value：图片
        self.images["L"] = pygame.image.load("images/tankL.gif")
        self.images["R"] = pygame.image.load("images/tankR.gif")
        self.images["U"] = pygame.image.load("images/tankU.gif")
        self.images["D"] = pygame.image.load("images/tankD.gif")
        self.image = self.images[self.direction]  # 坦克的图片由方向决定
        self.rect = self.image.get_rect()
        self.rect.left = left
        self.rect.top = top
        self.live = True  # 决定坦克是否消灭了
        self.oldtop = self.rect.top
        self.oldleft = self.rect.left

    # 停留在原地的方法
    def stay(self):
        self.rect.top = self.oldtop
        self.rect.left = self.oldleft

    # 坦克移动的方法
    def move(self):
        if not self.stop:  # 如果坦克不是停止的
            self.oldleft = self.rect.left
            self.oldtop = self.rect.top
            if self.direction == "L":  # 如果坦克的方向向左，那么只需要改坦克的left就ok了，left在减小
                if self.rect.left > 0:  # 判断坦克是否已经在屏幕左边的边界上了，不在则向左边移动，在则不移动
                    self.rect.left -= self.speed
                else:
                    self.rect.left = 0
            elif self.direction == "R":  # 如果坦克方向向右，坦克的right增加
                if self.rect.right < TankMain.width:  # 判断坦克是否在屏幕的最右边，不在则向右边移动，在的话就不能往右移动了
                    self.rect.right += self.speed
                else:
                    self.rect.right = TankMain.width
            elif self.direction == "D":  # 如果坦克方向向下，坦克的bottom增加
                if self.rect.bottom < TankMain.height:  # 判断坦克是否在屏幕最底部，不在底部往下移动，在则不动
                    self.rect.top += self.speed
                else:
                    self.rect.bottom = TankMain.height
            elif self.direction == "U":  # 如果坦克方向向上，坦克的top减小
                if self.rect.top > 0:  # 判断坦克是否在屏幕顶部，不在顶部往上移动，在则不动
                    self.rect.top -= self.speed
                else:
                    self.rect.top = 0

    def fire(self):
        m = Missile(self.screen, self)
        return m


# 我方坦克的类
class My_Tank(Tank):

    def __init__(self, screen):
        super().__init__(screen, 275, 400)  # 创建一个我放坦克，坦克显示在屏幕的中下部位置
        self.images = {}  # 坦克的所有图片，key：方向，value：图片
        self.images["L"] = pygame.image.load("images/mytankL.gif")
        self.images["R"] = pygame.image.load("images/mytankR.gif")
        self.images["U"] = pygame.image.load("images/mytankU.gif")
        self.images["D"] = pygame.image.load("images/mytankD.gif")
        self.stop = True
        self.live = True

    def hit_enemy_missile(self):
        hit_list = pygame.sprite.spritecollide(self, TankMain.enemy_missile_list, False)
        for m in hit_list:  # 我方坦克中弹了
            m.live = False
            TankMain.enemy_missile_list.remove(m)
            self.live = False
            explode = Explode(self.screen, self.rect)
            TankMain.explode_list.append(explode)


# 敌方坦克的类
class Enemy_Tank(Tank):

    def __init__(self, screen):
        super().__init__(screen, randint(1, 5) * 100, 200)
        self.speed = 4
        self.step = 8  # 坦克按照某个方向移动的步数
        self.get_random_direction()

    def get_random_direction(self):
        r = randint(0, 4)  # 得到一个坦克移动方向和停止的随机数
        if r == 4:
            self.stop = True
        elif r == 0:
            self.direction = "L"
            self.stop = False
        elif r == 1:
            self.direction = "R"
            self.stop = False
        elif r == 2:
            self.direction = "D"
            self.stop = False
        elif r == 3:
            self.direction = "U"
            self.stop = False

    # 敌方坦克，按照一个确定随机方向，连续移动6步，才能再次改变方向
    def random_move(self):
        if self.live:
            if self.step == 0:
                self.get_random_direction()
                self.step = 6
            else:
                self.move()
                self.step -= 1

    def random_fire(self):
        r = randint(0, 50)
        if r == 10 or r == 20 or r == 30 or r == 40:
            m = self.fire()
            TankMain.enemy_missile_list.add(m)
        else:
            return


# 炮弹类
class Missile(BaseItem):
    width = 12
    height = 12

    def __init__(self, screen, tank):
        super().__init__(screen)
        self.tank = tank
        self.direction = tank.direction  # 炮弹的方向由所发射的坦克方向决定
        self.speed = 12  # 坦克移动的速度
        self.images = {}  # 坦克的所有图片，key：方向，value：图片
        self.images["L"] = pygame.image.load("images/missileL.gif")
        self.images["R"] = pygame.image.load("images/missileR.gif")
        self.images["U"] = pygame.image.load("images/missileU.gif")
        self.images["D"] = pygame.image.load("images/missileD.gif")
        self.image = self.images[self.direction]  # 坦克的图片由方向决定
        self.rect = self.image.get_rect()
        self.rect.left = tank.rect.left + (tank.width - self.width) / 2
        self.rect.top = tank.rect.top + (tank.height - self.height) / 2
        self.live = True  # 决定炮弹是否消灭了
        self.good = False  #

    def move(self):
        if self.live:  # 如果炮弹是存在的
            if self.direction == "L":  # 如果坦克的方向向左，那么只需要改坦克的left就ok了，left在减小
                if self.rect.left > 0:  # 判断坦克是否已经在屏幕左边的边界上了，不在则向左边移动，在则不移动
                    self.rect.left -= self.speed
                else:
                    self.live = False
            elif self.direction == "R":  # 如果坦克方向向右，坦克的right增加
                if self.rect.right < TankMain.width:  # 判断坦克是否在屏幕的最右边，不在则向右边移动，在的话就不能往右移动了
                    self.rect.right += self.speed
                else:
                    self.live = False
            elif self.direction == "D":  # 如果坦克方向向下，坦克的bottom增加
                if self.rect.bottom < TankMain.height:  # 判断坦克是否在屏幕最底部，不在底部往下移动，在则不动
                    self.rect.top += self.speed
                else:
                    self.live = False
            elif self.direction == "U":  # 如果坦克方向向上，坦克的top减小
                if self.rect.top > 0:  # 判断坦克是否在屏幕顶部，不在顶部往上移动，在则不动
                    self.rect.top -= self.speed
                else:
                    self.live = False

    # 炮弹击中坦克：我方炮弹击中敌方坦克；敌方炮弹击中我方坦克
    def hit_tank(self):
        if self.good:  # 如果炮弹是我方的炮弹
            hit_list = pygame.sprite.spritecollide(self, TankMain.enemy_list, False)
            for e in hit_list:
                e.live = False
                TankMain.enemy_list.remove(e)  # 如果敌方坦克被击中，则从列表中删除
                self.live = False
                explode = Explode(self.screen, e.rect)  # 产生了一个爆炸对象
                TankMain.explode_list.append(explode)


# 爆炸类
class Explode(BaseItem):

    def __init__(self, screen, rect):
        super().__init__(screen)
        self.live = True
        self.images = [pygame.image.load("images/0.gif"), \
                       pygame.image.load("images/1.gif"), \
                       pygame.image.load("images/2.gif"), \
                       pygame.image.load("images/3.gif"), \
                       pygame.image.load("images/4.gif"), \
                       pygame.image.load("images/5.gif"), \
                       pygame.image.load("images/6.gif"), \
                       pygame.image.load("images/7.gif"), \
                       pygame.image.load("images/8.gif"), \
                       pygame.image.load("images/9.gif"), \
                       pygame.image.load("images/10.gif")]
        self.step = 0
        self.rect = rect  # 爆炸的位置和发生爆炸前，炮弹碰到的坦克位置一样。在构建爆炸的时候把坦克的rect传递进来

    # display方法在整个游戏运行过程中，循环调用，每隔0.1秒调用一次
    def display(self):
        if self.live:
            if self.step == len(self.images):  # 最后一张爆炸图片已经显示了
                self.live = False
            else:
                self.image = self.images[self.step]
                self.screen.blit(self.image, self.rect)
                self.step += 1
        else:
            pass


# 游戏中的墙
class Wall(BaseItem):
    def __init__(self, screen, left, top, width, height):
        super().__init__(screen)
        self.rect = Rect(left, top, width, height)
        self.color = (255, 0, 0)

    def display(self):
        self.screen.fill(self.color, self.rect)

    def hit_other(self):
        # 我方坦克不能穿过墙
        if TankMain.my_tank:
            is_hit = pygame.sprite.collide_rect(self, TankMain.my_tank)
            if is_hit:
                TankMain.my_tank.stop = True
                TankMain.my_tank.stay()     # 当发生了碰撞后，回到上一次的位置（由于每次移动是5px，所以肉眼看不出移动的效果）
        # 敌方坦克不能穿过墙
        if len(TankMain.enemy_list) != 0:
            hit_list = pygame.sprite.spritecollide(self, TankMain.enemy_list, False)
            for e in hit_list:
                e.stop = True
                e.stay()
        # 我方炮弹不能穿过墙
        if len(TankMain.my_tank_missile_list) != 0:
            hit_list = pygame.sprite.spritecollide(self, TankMain.my_tank_missile_list, False)
            for e in hit_list:
                TankMain.my_tank_missile_list.remove(e)
        # 敌方炮弹不能穿过墙
        if len(TankMain.enemy_missile_list) != 0:
            hit_list = pygame.sprite.spritecollide(self, TankMain.enemy_missile_list, False)
            for e in hit_list:
                TankMain.enemy_missile_list.remove(e)


game = TankMain()
game.startGame()
