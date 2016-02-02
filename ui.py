import libtcodpy as tcod
from config import SCREEN_WIDTH, SCREEN_HEIGHT, SCREEN_SIZE, CONWAY_SPEED,\
    MAX_FPS, VERSION
import game
import copy

controls = [
    ['w', 'a', 's', 'd'],
    [tcod.KEY_UP, tcod.KEY_LEFT,
        tcod.KEY_DOWN, tcod.KEY_RIGHT],
    ['t', 'f', 'g', 'h'],
    ['i', 'j', 'k', 'l'],
]

number_keys = [tcod.KEY_0, tcod.KEY_1, tcod.KEY_2, tcod.KEY_3, tcod.KEY_4,
               tcod.KEY_5, tcod.KEY_6, tcod.KEY_7, tcod.KEY_8, tcod.KEY_9]


def get_key(key):
    if key.vk == tcod.KEY_CHAR:
        return chr(key.c)
    else:
        return key.vk


def whole_number_menu(var, title, min_var=None):
    """A menu to change the value of a whole number x"""
    w, h = SCREEN_WIDTH, SCREEN_HEIGHT
    window = tcod.console_new(w, h)
    key = tcod.console_check_for_keypress()
    while not key.vk in (tcod.KEY_ENTER, tcod.KEY_ESCAPE):
        tcod.console_clear(window)
        x = SCREEN_WIDTH / 2
        y = SCREEN_HEIGHT / 2
        tcod.console_set_foreground_color(window, tcod.yellow)
        tcod.console_print_center(window, x, y, tcod.BKGND_NONE, title)
        tcod.console_set_foreground_color(window, tcod.white)
        tcod.console_print_center(window, x, y + 2, tcod.BKGND_NONE, str(var))

        tcod.console_set_foreground_color(window, tcod.grey)
        tcod.console_print_center(window, x, y + 4, tcod.BKGND_NONE,
                                  'Use arrows or number keys')
        tcod.console_print_center(window, x, y + 5, tcod.BKGND_NONE,
                                  'Press Enter or Escape to return')
        tcod.console_blit(window, 0, 0, w, h, 0, 0, 0, 1.0, 1.0)
        tcod.console_flush()

        key = tcod.console_wait_for_keypress(True)

        if key.vk == tcod.KEY_LEFT:
            # conway speed can update every frame at fastest
            var = max(var - 1, 1)
        elif key.vk == tcod.KEY_BACKSPACE:
            string_var = str(var)[:-1]
            if string_var == '':
                var = 0
            else:
                var = int(string_var)
        elif key.vk in number_keys:
            str_number = str(number_keys.index(key.vk))
            var = int(str(var) + str_number)
        elif key.vk == tcod.KEY_RIGHT:
            var += 1
    if min_var is None or var >= min_var:
        return var
    else:
        return whole_number_menu(var, title, min_var)


def handle_main_menu():
    # default players
    players = [game.Player((0, 0), (1, 0), tcod.red,
                           controls=controls[0]),
               game.Player((-1, -1), (-1, 0),
                           tcod.cyan),  # cyan is used instead of blue for
               # legibility and brightness
               game.Player((-1, 0), (0, 1),
                           tcod.green),
               game.Player((0, -1), (0, -1),
                           tcod.yellow),
               ]

    conway_speed = CONWAY_SPEED
    map_width, map_height = SCREEN_SIZE
    max_fps = MAX_FPS

    while not tcod.console_is_window_closed():
        tcod.console_clear(0)
        tcod.console_set_foreground_color(0, tcod.white)
        tcod.console_print_center(0, SCREEN_WIDTH / 2, 2, tcod.BKGND_NONE,
                                  'Conway\'s Game of Tron')
        tcod.console_set_foreground_color(0, tcod.grey)
        tcod.console_print_center(0, SCREEN_WIDTH / 2, 3, tcod.BKGND_NONE,
                                  'by Spferical (spferical@gmail.com)')
        tcod.console_print_center(0, SCREEN_WIDTH / 2, 4, tcod.BKGND_NONE,
                                  'Version ' + VERSION)
        tcod.console_set_foreground_color(0, tcod.white)
        tcod.console_print_left(0, 2, 6, tcod.BKGND_NONE,
                                '(a) Play')
        tcod.console_print_left(0, 2, 7, tcod.BKGND_NONE,
                                '(b) Exit')
        player_keys = ['c', 'd', 'e', 'f']
        y = 9
        x = 2
        playernum = -1
        for player in players:
            y += 1
            playernum += 1
            k = player_keys[playernum]
            if not player.dead:
                tcod.console_set_foreground_color(0, player.color)
            else:
                tcod.console_set_foreground_color(0, tcod.white)
            if not player.dead and player.controls:
                if player.controls == [tcod.KEY_UP, tcod.KEY_LEFT,
                                       tcod.KEY_DOWN, tcod.KEY_RIGHT]:
                    str_controls = '[arrow keys]'
                else:
                    str_controls = str(player.controls)
                text = '(' + k + ') ' + str(playernum +
                                            1) + ' Player ' + str_controls
            elif not player.dead and not player.controls:
                text = '(' + k + ') ' + str(playernum + 1) + ' CPU'
            else:
                text = '(' + k + ') ' + str(playernum + 1) + ' Not Playing'
            tcod.console_print_left(0, x, y, tcod.BKGND_NONE, text)

        tcod.console_set_foreground_color(0, tcod.white)
        tcod.console_print_left(0, 2, 15, tcod.BKGND_NONE,
                                '(g) Conway speed: ' + str(conway_speed))
        tcod.console_print_left(0, 2, 17, tcod.BKGND_NONE,
                                '(h) Map width: ' + str(map_width))
        tcod.console_print_left(0, 2, 18, tcod.BKGND_NONE,
                                '(i) Map height: ' + str(map_height))
        tcod.console_print_left(0, 2, 20, tcod.BKGND_NONE,
                                '(j) FPS: ' + str(max_fps))

        tcod.console_flush()

        raw_key = tcod.console_wait_for_keypress(tcod.KEY_PRESSED)
        key = get_key(raw_key)
        if key == 'a':
            game.play(copy.deepcopy(players), conway_speed,
                     (map_width, map_height), max_fps)
        elif key == 'b':
            break
        elif key in player_keys:
            p = player_keys.index(key)
            player = players[p]
            if player.dead:
                player.dead = False
                player.controls = controls[p]
            elif player.controls:
                player.controls = None
            else:
                player.dead = True
        elif key == 'g':
            conway_speed = whole_number_menu(
                conway_speed, 'The Conway simulation will update every how many frames?')
        elif key == 'h':
            map_width = whole_number_menu(
                map_width, 'How wide should the map be?', min_var=1)
        elif key == 'i':
            map_height = whole_number_menu(
                map_height, 'How tall should the map be?', min_var=1)
        elif key == 'j':
            max_fps = whole_number_menu(
                max_fps, 'How many frames per second should the game run at?')
        elif key == tcod.KEY_ESCAPE:
            break
