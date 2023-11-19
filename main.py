import chess
import pygame
import subprocess
import communicate
import engine

SQUARE_SIZE = 85
FPS = 60
clock = pygame.time.Clock()

pygame.init()
size = width, height = 8 * SQUARE_SIZE, 8 * SQUARE_SIZE  # Size of the window
screen = pygame.display.set_mode(size)

board = chess.Board()
print(board)

piece_images = {}

# Define the file names for each piece
piece_files = {
    chess.Piece(chess.PAWN, chess.WHITE): "white_pawn.png",
    chess.Piece(chess.ROOK, chess.WHITE): "white_rook.png",
    chess.Piece(chess.KNIGHT, chess.WHITE): "white_knight.png",
    chess.Piece(chess.BISHOP, chess.WHITE): "white_bishop.png",
    chess.Piece(chess.QUEEN, chess.WHITE): "white_queen.png",
    chess.Piece(chess.KING, chess.WHITE): "white_king.png",
    chess.Piece(chess.PAWN, chess.BLACK): "black_pawn.png",
    chess.Piece(chess.ROOK, chess.BLACK): "black_rook.png",
    chess.Piece(chess.KNIGHT, chess.BLACK): "black_knight.png",
    chess.Piece(chess.BISHOP, chess.BLACK): "black_bishop.png",
    chess.Piece(chess.QUEEN, chess.BLACK): "black_queen.png",
    chess.Piece(chess.KING, chess.BLACK): "black_king.png"
}

# Load the images
for piece, file_name in piece_files.items():
    image_path = f"data/images/{file_name}"
    piece_images[str(piece)] = pygame.image.load(image_path)

pygame.mixer.init()
move_self = pygame.mixer.Sound("data/sounds/move-self.mp3")
move_check = pygame.mixer.Sound("data/sounds/move-check.mp3")
capture = pygame.mixer.Sound("data/sounds/capture.mp3")
game_end = pygame.mixer.Sound("data/sounds/game-end.mp3")
promote = pygame.mixer.Sound("data/sounds/promote.mp3")
castle = pygame.mixer.Sound("data/sounds/castle.mp3")


def draw_board(screen):
    colors = [pygame.Color("white"), pygame.Color("gray")]
    for row in range(8):
        for col in range(8):
            color = colors[(row + col) % 2]
            pygame.draw.rect(screen, color, pygame.Rect(
                col * SQUARE_SIZE, row * SQUARE_SIZE, SQUARE_SIZE, SQUARE_SIZE))


def draw_pieces(screen, board, piece_images, SQUARE_SIZE, is_white, dragging_piece=None, dragging_from_square=None):
    for square in chess.SQUARES:
        piece = board.piece_at(square)
        if piece and not (dragging_piece and square == dragging_from_square):
            if is_white:
                flipped_square = square
            else:
                flipped_square = chess.square(
                    7 - chess.square_file(square), 7 - chess.square_rank(square))

            # Calculate the top-left corner of the square
            x = (flipped_square % 8) * SQUARE_SIZE
            y = (7 - flipped_square // 8) * SQUARE_SIZE

            # Get the size of the piece image
            piece_image = piece_images[str(piece)]
            piece_width, piece_height = piece_image.get_size()

            # Adjust x and y to center the piece
            x += (SQUARE_SIZE - piece_width) // 2
            y += (SQUARE_SIZE - piece_height) // 2

            # Draw the piece on the board
            screen.blit(piece_image, (x, y))


def get_position_when_dragging():
    mouse_x, mouse_y = pygame.mouse.get_pos()
    return (mouse_x - SQUARE_SIZE // 2, mouse_y - SQUARE_SIZE // 2)


def selection_screen(screen):
    font = pygame.font.Font(None, 36)
    text_white = font.render('Play as White', True, pygame.Color('Black'))
    text_black = font.render('Play as Black', True, pygame.Color('Black'))

    white_button = text_white.get_rect(center=(width // 2, height // 3))
    black_button = text_black.get_rect(center=(width // 2, 2 * height // 3))

    running = True
    global my_turn
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
                return None
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if white_button.collidepoint(event.pos):
                    my_turn = True
                    return True  # True for white
                elif black_button.collidepoint(event.pos):
                    my_turn = False
                    return False  # False for black

        screen.fill(pygame.Color('White'))
        screen.blit(text_white, white_button)
        screen.blit(text_black, black_button)
        pygame.display.flip()


def promote_pawn(board, screen, move, start_square, end_square, player_is_white):
    pawn_color = board.piece_at(start_square).color
    promotion_piece = promotion_screen(screen, pawn_color, SQUARE_SIZE, chess.square_rank(
        end_square), chess.square_file(end_square), player_is_white)
    if promotion_piece is not None:
        move = chess.Move(
            move.from_square, move.to_square, promotion_piece)
        promote.play()


def promotion_screen(screen, piece_color, SQUARE_SIZE, promotion_rank, promotion_file, is_white):
    # Load images for promotion pieces
    if piece_color == chess.WHITE:
        queen_img = pygame.image.load("data/images/white_queen.png")
        rook_img = pygame.image.load("data/images/white_rook.png")
        bishop_img = pygame.image.load("data/images/white_bishop.png")
        knight_img = pygame.image.load("data/images/white_knight.png")
    else:
        queen_img = pygame.image.load("data/images/black_queen.png")
        rook_img = pygame.image.load("data/images/black_rook.png")
        bishop_img = pygame.image.load("data/images/black_bishop.png")
        knight_img = pygame.image.load("data/images/black_knight.png")

    # Determine the popup location based on the promotion square
    if is_white:
        promotion_rank = 7 - promotion_rank

    popup_width = SQUARE_SIZE
    popup_height = 4 * SQUARE_SIZE
    # Align the top of the popup with the top of the promotion square
    popup_y = promotion_rank * SQUARE_SIZE
    # Align the popup
    popup_x = (promotion_file) * SQUARE_SIZE

    # Ensure the popup stays within the screen bounds
    popup_x = max(0, min(popup_x, width - popup_width))
    popup_y = max(0, min(popup_y, height - popup_height))

    # Assuming all images are the same size
    image_width, image_height = queen_img.get_width(), queen_img.get_height()

    # Calculate horizontal centering within the square
    center_x = popup_x + (SQUARE_SIZE - image_width) // 2

    # Get rects for each image within the pop-up, stacked vertically and centered
    queen_rect = queen_img.get_rect(topleft=(center_x, popup_y))
    rook_rect = rook_img.get_rect(topleft=(center_x, popup_y + SQUARE_SIZE))
    bishop_rect = bishop_img.get_rect(
        topleft=(center_x, popup_y + 2 * SQUARE_SIZE))
    knight_rect = knight_img.get_rect(
        topleft=(center_x, popup_y + 3 * SQUARE_SIZE))

    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
                return None
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if queen_rect.collidepoint(event.pos):
                    return chess.QUEEN
                elif rook_rect.collidepoint(event.pos):
                    return chess.ROOK
                elif bishop_rect.collidepoint(event.pos):
                    return chess.BISHOP
                elif knight_rect.collidepoint(event.pos):
                    return chess.KNIGHT

        # Draw the pop-up background
        pygame.draw.rect(screen, pygame.Color('White'),
                         (popup_x, popup_y, popup_width, popup_height))

        screen.blit(queen_img, queen_rect)
        screen.blit(rook_img, rook_rect)
        screen.blit(bishop_img, bishop_rect)
        screen.blit(knight_img, knight_rect)

        pygame.display.flip()


def check_game_over(board):
    if board.is_checkmate():
        return "Checkmate"
    elif board.is_stalemate():
        return "Stalemate"
    elif board.is_insufficient_material():
        return "Draw due to insufficient material"
    elif board.can_claim_draw():
        return "Draw"
    return None


def game_over_screen(screen):
    font = pygame.font.Font(None, 36)

    # Game over message
    text = font.render(outcome, True, pygame.Color('Black'))
    text_rect = text.get_rect(center=(width // 2, height // 4))

    # Selection screen buttons
    text_white = font.render('Play as White', True, pygame.Color('Black'))
    text_black = font.render('Play as Black', True, pygame.Color('Black'))
    white_button = text_white.get_rect(center=(width // 2, height // 2))
    black_button = text_black.get_rect(center=(width // 2, 3 * height // 4))

    while True:
        screen.fill(pygame.Color('White'))
        screen.blit(text, text_rect)
        screen.blit(text_white, white_button)
        screen.blit(text_black, black_button)
        pygame.display.flip()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False  # Quit the game

            elif event.type == pygame.MOUSEBUTTONDOWN:
                if white_button.collidepoint(event.pos):
                    global my_turn
                    my_turn = True
                    return True  # Restart and play as White

                elif black_button.collidepoint(event.pos):
                    my_turn = False
                    return False  # Restart and play as Black


def set_move(event, selected_square_col, selected_square_row, player_is_white):
    new_x, new_y = event.pos
    new_col, new_row = new_x // SQUARE_SIZE, 7 - new_y // SQUARE_SIZE
    if not player_is_white:  # Flip coordinates for black player
        new_col = 7 - new_col
        new_row = 7 - new_row
    start_square = chess.square(
        selected_square_col, selected_square_row)
    end_square = chess.square(new_col, new_row)
    if new_col > 7 or new_row > 7 or new_col < 0 or new_row < 0:
        end_square = chess.square(
            selected_square_col, selected_square_row)
    return start_square, end_square, chess.Move(start_square, end_square)


def highlight_last_move(screen, last_move_start_square, last_move_end_square, SQUARE_SIZE, is_white):
    if last_move_start_square is None or last_move_end_square is None:
        return
    if last_move_start_square is not None and last_move_end_square is not None:
        # Choose a suitable highlight color
        highlight_color = pygame.Color('green')

        # Calculate positions for start and end squares
        start_col, start_row = chess.square_file(
            last_move_start_square), chess.square_rank(last_move_start_square)
        end_col, end_row = chess.square_file(
            last_move_end_square), chess.square_rank(last_move_end_square)

        # Flip for black player's perspective
        if is_white:
            start_row = 7 - start_row
            end_row = 7 - end_row
        else:
            start_col = 7 - start_col
            end_col = 7 - end_col

        # Draw highlights
        pygame.draw.rect(screen, highlight_color, pygame.Rect(
            start_col * SQUARE_SIZE, start_row * SQUARE_SIZE, SQUARE_SIZE, SQUARE_SIZE), 5)
        pygame.draw.rect(screen, highlight_color, pygame.Rect(
            end_col * SQUARE_SIZE, end_row * SQUARE_SIZE, SQUARE_SIZE, SQUARE_SIZE), 5)


def draw_legal_moves(legal_moves, screen, player_is_white):
    for move in legal_moves:
        end_square = move.to_square
        end_col, end_row = chess.square_file(
            end_square), 7 - chess.square_rank(end_square)
        if not player_is_white:
            end_col = 7 - end_col
            end_row = 7 - end_row
        center_x = end_col * SQUARE_SIZE + SQUARE_SIZE // 2
        center_y = end_row * SQUARE_SIZE + SQUARE_SIZE // 2
        pygame.draw.circle(screen, pygame.Color(
            'Green'), (center_x, center_y), SQUARE_SIZE // 6)


def check_special_event(board, move):
    if move in board.legal_moves:
        if board.piece_at(move.from_square).piece_type == chess.PAWN:
            if move.to_square in chess.SquareSet(chess.BB_RANK_1 | chess.BB_RANK_8):
                promote_pawn(board, screen, move,
                             start_square, end_square, player_is_white)
                return True
        if board.is_capture(move):
            capture.play()
            return True


def play_sound(board, move, special_event_occurred):
    # Check game conditions after the move
    if board.outcome():
        game_end.play()
        special_event_occurred = True
    elif board.is_check():
        move_check.play()
        special_event_occurred = True
    elif board.is_castling(move):
        castle.play()
        special_event_occurred = True

    if not special_event_occurred:  # Play default move sound if no special event
        move_self.play()


def communicate_with_engine(board):
    fen_string = board.fen()
    legal_moves = ' '.join(str(move) for move in board.legal_moves)
    # Separating FEN and moves by a newline
    input_data = fen_string + "\n" + legal_moves

    cpp_executable_path = "./engine"

    process = subprocess.Popen(
        cpp_executable_path,
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        text=True
    )

    stdout, stderr = process.communicate(input_data)


running = True
# Variables for drag and drop
dragging = False
selected_piece = None
selected_piece_position = None
selected_square_col = None
selected_square_row = None
legal_moves = None
last_move_start_square = None
last_move_end_square = None
my_turn = True

player_is_white = selection_screen(screen)
if player_is_white is None:
    pygame.quit()


while running:
    clock.tick(FPS)
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        # click and select piece
        if event.type == pygame.MOUSEBUTTONDOWN:
            x, y = event.pos
            col = x // SQUARE_SIZE
            row = 7 - y // SQUARE_SIZE
            if not player_is_white:  # Flip coordinates for black player
                col = 7 - col
                row = 7 - row
            square = chess.square(col, row)
            piece = board.piece_at(square)
            if piece:
                dragging = True
                selected_piece = piece
                selected_piece_position = (x, y)
                selected_square_col = col
                selected_square_row = row
                legal_moves = [move for move in board.legal_moves if move.from_square == chess.square(
                    selected_square_col, selected_square_row)]

        # release piece
        if event.type == pygame.MOUSEBUTTONUP and dragging:
            start_square, end_square, move = set_move(
                event, selected_square_col, selected_square_row, player_is_white)

            if board.piece_at(start_square).piece_type == chess.PAWN and \
                    (chess.square_rank(end_square) == 0 or chess.square_rank(end_square) == 7):
                move = chess.Move(start_square, end_square,
                                  promotion=chess.QUEEN)

            special_event_occurred = False
            if move in board.legal_moves:
                if board.piece_at(move.from_square).piece_type == chess.PAWN:
                    if move.to_square in chess.SquareSet(chess.BB_RANK_1 | chess.BB_RANK_8):
                        promote_pawn(board, screen, move,
                                     start_square, end_square, player_is_white)
                        special_event_occurred = True
                if board.is_capture(move):
                    capture.play()
                    special_event_occurred = True

                board.push(move)
                print(move)
                my_turn = False
                # communicate_with_engine(board)
                # communicate.get_best_move(board)

                last_move_start_square = move.from_square
                last_move_end_square = move.to_square

                play_sound(board, move, special_event_occurred)

            print(board)
            dragging = False
            selected_piece = None
            selected_piece_position = None
            legal_moves = None

    if dragging and selected_piece:
        selected_piece_position = get_position_when_dragging()

    outcome = check_game_over(board)
    if outcome:
        restart = game_over_screen(screen)
        if restart:
            board.reset()  # Reset the board for a new game
            last_move_end_square = None
            last_move_start_square = None
        else:
            running = False

    draw_board(screen)
    highlight_last_move(screen, last_move_start_square,
                        last_move_end_square, SQUARE_SIZE, player_is_white)
    draw_pieces(screen, board, piece_images, SQUARE_SIZE, player_is_white, selected_piece,
                chess.square(selected_square_col, selected_square_row) if dragging else None)
    if dragging and legal_moves:
        draw_legal_moves(legal_moves, screen, player_is_white)
    if dragging and selected_piece:
        screen.blit(piece_images[str(selected_piece)], selected_piece_position)
    pygame.display.flip()
    if not my_turn:
        move = engine.get_best_move(board, 5)
        board.push(move)
        special_event_occurred = check_special_event(board, move)
        play_sound(board, move, special_event_occurred)
        last_move_start_square = move.from_square
        last_move_end_square = move.to_square
        highlight_last_move(screen, last_move_start_square,
                            last_move_end_square, SQUARE_SIZE, player_is_white)
        my_turn = True
