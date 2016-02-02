import copy
import libtcodpy as tcod
from config import GAME_TITLE, SCREEN_SIZE, CONWAY_SPEED, MAX_FPS
import ui
import random

# controls in order: up, left, down, right
player_1_controls = [tcod.KEY_UP, tcod.KEY_LEFT,
                     tcod.KEY_DOWN, tcod.KEY_RIGHT]
# possible directions, in (dx, dy) format
directions = [
    (0, -1),  # up
    (-1, 0),  # left
    (0, 1),  # down
    (1, 0),  # right
]

players = []
map_size = (0, 0)
blank_map = [[False for y in range(map_size[1])]
             for x in range(map_size[0])]
game_map = copy.copy(blank_map)
winner = None
alive = False


class Player:
    def __init__(self, pos, direction, color,
                 controls=None):
        self.x, self.y = pos
        self.dx, self.dy = direction
        self.color = color
        self.controls = controls
        self.dead = False

    def update(self):
        self.x += self.dx
        self.y += self.dy


def handle_keys():
    raw_key = tcod.console_check_for_keypress(tcod.KEY_PRESSED)
    while raw_key.vk != tcod.KEY_NONE:
        key = ui.get_key(raw_key)
        for player in players:
            if player.controls:
                if key in player.controls:
                    m = player.controls.index(key)
                    d = directions[m]
                    # make sure player isn't turning backwards, running into
                    # his own trail
                    backwards = (player.dx * -1, player.dy * -1)
                    if d != backwards:
                        player.dx, player.dy = d
        if key == tcod.KEY_ESCAPE:
            return 'exit'
        raw_key = tcod.console_check_for_keypress(tcod.KEY_PRESSED)


def update_ai():
    for player in players:
        if not player.controls:
            if random.randint(0, 10) == 0:
                player.dx, player.dy = directions[random.randint(0, 3)]
            turn = random.choice([-1, 1])  # ai either turns right or left
            for i in range(4):
                dx, dy = (player.x + player.dx, player.y + player.dy)
                if not is_tile_blocked((dx, dy)):
                    break
                else:
                    newindex = directions.index((player.dx, player.dy))
                    newindex += turn
                    if newindex == 4:
                        newindex = 0
                    player.dx, player.dy = directions[newindex]


def is_tile_blocked((x, y)):
    map_width, map_height = map_size
    if (x < 0 or x >= map_width or
            y < 0 or y >= map_height):
        return 2
    elif game_map[x][y]:
        return 1


def update_players():
    for player in players:
        if not player.dead:
            player.x += player.dx
            player.y += player.dy
            if is_tile_blocked((player.x, player.y)):
                player.dead = True
            else:
                game_map[player.x][player.y] = player.color

player_chars = {
    # direction : char,
    (1, 0): tcod.CHAR_ARROW2_E,
    (-1, 0): tcod.CHAR_ARROW2_W,
    (0, -1): tcod.CHAR_ARROW2_N,
    (0, 1): tcod.CHAR_ARROW2_S,
}


def render():
    for player in players:
        if not player.dead:
            tcod.console_put_char_ex(0, player.x, player.y,
                                     player_chars[(player.dx, player.dy)],
                                     tcod.black, player.color)
    if winner:
        tcod.console_set_foreground_color(0, winner.color)
        tcod.console_print_left(0, 0, map_size[1] - 1, tcod.BKGND_NONE,
                                'Player ' + str(players.index(winner) + 1) +
                                ' is the winner!')
    tcod.console_flush()

    # erase player arrows from their old positions
    for player in players:
        if not player.dead:
            tcod.console_put_char(0, player.x, player.y, ' ', tcod.BKGND_NONE)


def render_entire_map():
    map_width, map_height = map_size
    for x in range(map_width):
        for y in range(map_height):
            tcod.console_set_back(0, x, y, game_map[x][y])


def update_conway():
    global game_map
    map_width, map_height = map_size
    new_map = copy.deepcopy(blank_map)
    for x in range(map_width):
        for y in range(map_height):
            adjacent = get_adjacent(x, y)
            alive = len(adjacent) == 3 or (
                len(adjacent) == 2 and game_map[x][y])
            if alive:
                final_color = tcod.white
                i = 0
                for color in adjacent:
                    i += 1
                    final_color = tcod.color_lerp(final_color, color,
                                                  1.0 / i)
                # color = most_common(adjacent)
                new_map[x][y] = final_color
    game_map = new_map


def get_adjacent(x, y):
    global game_map
    cells = []
    for dx in (-1, 0, 1):
        for dy in (-1, 0, 1):
            if not (dx == 0 and dy == 0):
                if is_tile_blocked((x + dx, y + dy)) == 1:
                    cells.append(game_map[x + dx][y + dy])
    return cells


def detect_winner():
    winner = None
    for player in players:
        if not player.dead:
            if winner:
                return None
            winner = player
    return winner


def play(game_players, conway_speed=CONWAY_SPEED,
         game_map_size=SCREEN_SIZE, fps=MAX_FPS):
    global players, game_map, map_size, blank_map, winner
    map_size = game_map_size
    blank_map = [[False for y in range(map_size[1])]
                 for x in range(map_size[0])]
    tcod.console_init_root(map_size[0], map_size[1],
                           GAME_TITLE, False)
    tcod.sys_set_fps(fps)
    tcod.console_clear(0)
    players = game_players
    # if player starting position is negative, wrap them on the other side
    # of the map
    for player in players:
        if player.x < 0:
            player.x = map_size[0] + player.x
        if player.y < 0:
            player.y = map_size[1] + player.y
    game_map = copy.deepcopy(blank_map)
    alive = True
    winner = None
    conway_update_timer = conway_speed
    while not tcod.console_is_window_closed() and alive:
        if handle_keys() == 'exit':
            alive = False
        update_ai()
        update_players()
        if not winner:
            winner = detect_winner()
        render()
        conway_update_timer -= 1
        if conway_update_timer == 0:
            conway_update_timer = conway_speed
            update_conway()
        render_entire_map()
    #(if the player closed the window, don't start a new window)
    if not tcod.console_is_window_closed():
        # after main loop, game exits to main menu
        # so set screen back to default size
        tcod.console_init_root(SCREEN_SIZE[0], SCREEN_SIZE[1],
                               GAME_TITLE, False)
        # reset fps to default for main menu
        #(main menu should always be quickly responsive)
        tcod.sys_set_fps(MAX_FPS)
