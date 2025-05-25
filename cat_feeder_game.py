import os
import random
import msvcrt
import time

# Game settings
GRID_WIDTH = 28
GRID_HEIGHT = 18
FISH_COUNT = 8
HAPPINESS_GOAL = 10

CAT_ICON = '😺'
FISH_ICON = '🐟'
DOG_ICON = '🐶'
MOUSE_ICON = '🐭'
MOUSE_COUNT = 3
# Use a fullwidth space character for matching width (works in Windows console with monospace fonts)
EMPTY_ICON = '　'  # U+3000 Ideographic space, 2-char wide

def clear_screen():
    os.system('cls')

def print_grid(cat_pos, fish_positions, dog_pos, mouse_positions):
    for y in range(GRID_HEIGHT):
        row = ''
        for x in range(GRID_WIDTH):
            if (x, y) == cat_pos:
                row += CAT_ICON
            elif (x, y) == dog_pos:
                row += DOG_ICON
            elif (x, y) in mouse_positions:
                row += MOUSE_ICON
            elif (x, y) in fish_positions:
                row += FISH_ICON
            else:
                row += EMPTY_ICON
        print(row)

def get_random_empty_position(cat_pos, fish_positions, extra_positions=None):
    if extra_positions is None:
        extra_positions = set()
    while True:
        pos = (random.randint(0, GRID_WIDTH-1), random.randint(0, GRID_HEIGHT-1))
        if pos != cat_pos and pos not in fish_positions and pos not in extra_positions:
            return pos

# Returns list of valid neighbor positions (including staying in place)
def get_valid_fish_moves(pos, cat_pos, fish_positions):
    neighbors = [
        (pos[0], pos[1]), # stay
        (pos[0]-1, pos[1]),
        (pos[0]+1, pos[1]),
        (pos[0], pos[1]-1),
        (pos[0], pos[1]+1),
    ]
    result = []
    for (x, y) in neighbors:
        if 0 <= x < GRID_WIDTH and 0 <= y < GRID_HEIGHT:
            if (x, y) != cat_pos and (x, y) not in fish_positions:
                result.append((x, y))
    # If all neighbors taken, fish can stay in place
    if (pos[0], pos[1]) not in result:
        result.append((pos[0], pos[1]))
    return result

def move_dog_towards_cat(dog_pos, cat_pos, fish_positions):
    # Dog moves one step closer to cat (no diagonal)
    dx = cat_pos[0] - dog_pos[0]
    dy = cat_pos[1] - dog_pos[1]
    new_x, new_y = dog_pos
    if abs(dx) > abs(dy):
        new_x += 1 if dx > 0 else -1 if dx < 0 else 0
    elif dy != 0:
        new_y += 1 if dy > 0 else -1
    # Avoid fish positions
    if (new_x, new_y) in fish_positions:
        # Try alternate axis
        if dx != 0 and (dog_pos[0] + (1 if dx > 0 else -1), dog_pos[1]) not in fish_positions:
            new_x = dog_pos[0] + (1 if dx > 0 else -1)
            new_y = dog_pos[1]
        elif dy != 0 and (dog_pos[0], dog_pos[1] + (1 if dy > 0 else -1)) not in fish_positions:
            new_x = dog_pos[0]
            new_y = dog_pos[1] + (1 if dy > 0 else -1)
        else:
            # Stay in place if blocked
            new_x, new_y = dog_pos
    # Stay within bounds
    new_x = max(0, min(GRID_WIDTH-1, new_x))
    new_y = max(0, min(GRID_HEIGHT-1, new_y))
    return (new_x, new_y)

def main():
    cat_pos = (GRID_WIDTH // 2, GRID_HEIGHT // 2)
    fish_positions = set()
    for _ in range(FISH_COUNT):
        fish_positions.add(get_random_empty_position(cat_pos, fish_positions))
    mouse_positions = set()
    for _ in range(MOUSE_COUNT):
        mouse_positions.add(get_random_empty_position(cat_pos, fish_positions, mouse_positions))
    dog_pos = get_random_empty_position(cat_pos, fish_positions, mouse_positions)
    happiness = 0
    moves_since_last_fish = 0
    MAX_MOVES_WITHOUT_FISH = 12
    dog_move_counter = 0

    print('Welcome to Cat Feeder!')
    print('Move the cat (😺) with Arrow keys. Collect fish (🐟) to feed your cat!')
    print('Catch mice (🐭) for double points!')
    print('Avoid the dog (🐶) chasing you!')
    print(f'Grid size: {GRID_WIDTH} x {GRID_HEIGHT}  |  Fishes and mice move now!')
    print('If you wander too long without feeding, happiness drops!')
    print(f'Reach happiness {HAPPINESS_GOAL} to win. Press Q to quit.')
    print('Press any key to start...')
    msvcrt.getch()

    happiness_decreased_msg = ''
    while True:
        clear_screen()
        print(f'Happiness: {happiness} / {HAPPINESS_GOAL}')
        print_grid(cat_pos, fish_positions, dog_pos, mouse_positions)
        if happiness_decreased_msg:
            print(happiness_decreased_msg)
            happiness_decreased_msg = ''
        print('Move (Arrow keys), or Q to quit: ')

        key = msvcrt.getch()
        # No sound on key press
        if key in (b'q', b'Q'):
            print('Thanks for playing!')
            break
        dx, dy = 0, 0
        if key == b'\xe0':  # Arrow key prefix
            arrow = msvcrt.getch()
            if arrow == b'H':  # Up
                dy = -1
            elif arrow == b'P':  # Down
                dy = 1
            elif arrow == b'K':  # Left
                dx = -1
            elif arrow == b'M':  # Right
                dx = 1
            else:
                continue
        else:
            continue
        new_x = max(0, min(GRID_WIDTH-1, cat_pos[0] + dx))
        new_y = max(0, min(GRID_HEIGHT-1, cat_pos[1] + dy))
        new_cat_pos = (new_x, new_y)

        moved = (new_cat_pos != cat_pos)
        # No play_move_sound()
        cat_pos = new_cat_pos
        caught_fish = False

        if cat_pos == dog_pos:
            clear_screen()
            print_grid(cat_pos, fish_positions, dog_pos, mouse_positions)
            print('Game Over! The dog caught your cat! 🐶😺')
            print('Thanks for playing!')
            break

        if cat_pos in mouse_positions:
            mouse_positions.remove(cat_pos)
            happiness += 2
            moves_since_last_fish = 0
            # No play_catch_sound()
            if happiness >= HAPPINESS_GOAL:
                clear_screen()
                print('Happiness: {} / {}'.format(happiness, HAPPINESS_GOAL))
                print_grid(cat_pos, fish_positions, dog_pos, mouse_positions)
                print('Congratulations! Your cat is happy and full 😺🎉')
                print('Thanks for playing!')
                break
            else:
                mouse_positions.add(get_random_empty_position(cat_pos, fish_positions, mouse_positions.union({dog_pos})))
        elif cat_pos in fish_positions:
            fish_positions.remove(cat_pos)
            happiness += 1
            moves_since_last_fish = 0
            caught_fish = True
            # No play_catch_sound()
            if happiness >= HAPPINESS_GOAL:
                clear_screen()
                print('Happiness: {} / {}'.format(happiness, HAPPINESS_GOAL))
                print_grid(cat_pos, fish_positions, dog_pos, mouse_positions)
                print('Congratulations! Your cat is happy and full 😺🎉')
                print('Thanks for playing!')
                break
            else:
                fish_positions.add(get_random_empty_position(cat_pos, fish_positions, mouse_positions.union({dog_pos})))
        else:
            if moved:
                moves_since_last_fish += 1
                if moves_since_last_fish > MAX_MOVES_WITHOUT_FISH:
                    if happiness > 0:
                        happiness -= 1
                        happiness_decreased_msg = 'Your cat is sad from hunger! (-1 happiness)'
                        # No play_decrease_sound()
                    else:
                        happiness_decreased_msg = 'Your cat is too hungry! (min happiness)'
                        # No play_decrease_sound()
                    moves_since_last_fish = 0

        # --- Move all fishes randomly ---
        new_fish_positions = set()
        for fish in fish_positions:
            valid_moves = get_valid_fish_moves(fish, cat_pos, new_fish_positions.union(fish_positions-{fish}).union(mouse_positions).union({dog_pos}))
            new_pos = random.choice(valid_moves)
            new_fish_positions.add(new_pos)
        fish_positions = new_fish_positions
        # --- Move all mice randomly ---
        new_mouse_positions = set()
        for mouse in mouse_positions:
            valid_moves = get_valid_fish_moves(mouse, cat_pos, new_mouse_positions.union(mouse_positions-{mouse}).union(fish_positions).union({dog_pos}))
            new_pos = random.choice(valid_moves)
            new_mouse_positions.add(new_pos)
        mouse_positions = new_mouse_positions
        # --- Move dog towards cat every other turn ---
        dog_move_counter += 1
        if dog_move_counter % 2 == 0:
            dog_pos = move_dog_towards_cat(dog_pos, cat_pos, fish_positions.union(mouse_positions))
        if dog_pos == cat_pos:
            clear_screen()
            print_grid(cat_pos, fish_positions, dog_pos, mouse_positions)
            print('Game Over! The dog caught your cat! 🐶😺')
            print('Thanks for playing!')
            break
        time.sleep(0.08)  # So accidental multiple moves less likely

if __name__ == "__main__":
    main()