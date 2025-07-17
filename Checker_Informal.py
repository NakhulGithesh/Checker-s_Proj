import pygame
import sys
import math
import copy

# Initialize Pygame
pygame.init()

# Constants
BOARD_SIZE = 8
SQUARE_SIZE = 80
SIDEBAR_WIDTH = 250
WINDOW_WIDTH = BOARD_SIZE * SQUARE_SIZE + SIDEBAR_WIDTH
WINDOW_HEIGHT = BOARD_SIZE * SQUARE_SIZE
FPS = 60

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
DARK_RED = (139, 0, 0)
LIGHT_BROWN = (240, 217, 181)
DARK_BROWN = (181, 136, 99)
BLUE = (0, 0, 255)
GREEN = (0, 255, 0)
GRAY = (128, 128, 128)
LIGHT_GRAY = (200, 200, 200)

# Piece constants
EMPTY = 0
RED_PIECE = 1
BLACK_PIECE = 2
RED_KING = 3
BLACK_KING = 4

class Piece:
    def __init__(self, color, is_king=False):
        self.color = color
        self.is_king = is_king
    
    def make_king(self):
        self.is_king = True
    
    def copy(self):
        return Piece(self.color, self.is_king)

class Board:
    def __init__(self):
        self.board = [[EMPTY for _ in range(BOARD_SIZE)] for _ in range(BOARD_SIZE)]
        self.red_pieces = 12
        self.black_pieces = 12
        self.red_kings = 0
        self.black_kings = 0
        self.setup_board()
    
    def setup_board(self):
        # Place black pieces (top of board)
        for row in range(3):
            for col in range(BOARD_SIZE):
                if (row + col) % 2 == 1:
                    self.board[row][col] = Piece(BLACK_PIECE)
        
        # Place red pieces (bottom of board)
        for row in range(5, 8):
            for col in range(BOARD_SIZE):
                if (row + col) % 2 == 1:
                    self.board[row][col] = Piece(RED_PIECE)
    
    def get_piece(self, row, col):
        return self.board[row][col]
    
    def move_piece(self, start_row, start_col, end_row, end_col):
        piece = self.board[start_row][start_col]
        self.board[start_row][start_col] = EMPTY
        self.board[end_row][end_col] = piece
        
        # Check for king promotion
        if piece.color == RED_PIECE and end_row == 0:
            piece.make_king()
            self.red_kings += 1
        elif piece.color == BLACK_PIECE and end_row == 7:
            piece.make_king()
            self.black_kings += 1
    
    def remove_piece(self, row, col):
        piece = self.board[row][col]
        if piece != EMPTY:
            if piece.color == RED_PIECE:
                self.red_pieces -= 1
                if piece.is_king:
                    self.red_kings -= 1
            else:
                self.black_pieces -= 1
                if piece.is_king:
                    self.black_kings -= 1
        self.board[row][col] = EMPTY
    
    def get_valid_moves(self, row, col):
        piece = self.board[row][col]
        if piece == EMPTY:
            return []
        
        moves = []
        
        # Define directions based on piece type
        if piece.is_king:
            directions = [(-1, -1), (-1, 1), (1, -1), (1, 1)]
        elif piece.color == RED_PIECE:
            directions = [(-1, -1), (-1, 1)]  # Red moves up
        else:
            directions = [(1, -1), (1, 1)]   # Black moves down
        
        # Check regular moves
        for dr, dc in directions:
            new_row, new_col = row + dr, col + dc
            if 0 <= new_row < BOARD_SIZE and 0 <= new_col < BOARD_SIZE:
                if self.board[new_row][new_col] == EMPTY:
                    moves.append((new_row, new_col))
        
        # Check jump moves
        jump_moves = self.get_jump_moves(row, col)
        moves.extend(jump_moves)
        
        return moves
    
    def get_jump_moves(self, row, col):
        piece = self.board[row][col]
        if piece == EMPTY:
            return []
        
        jump_moves = []
        
        # Define directions based on piece type
        if piece.is_king:
            directions = [(-1, -1), (-1, 1), (1, -1), (1, 1)]
        elif piece.color == RED_PIECE:
            directions = [(-1, -1), (-1, 1)]
        else:
            directions = [(1, -1), (1, 1)]
        
        for dr, dc in directions:
            # Check if there's an opponent piece to jump over
            jump_row, jump_col = row + dr, col + dc
            if 0 <= jump_row < BOARD_SIZE and 0 <= jump_col < BOARD_SIZE:
                jumped_piece = self.board[jump_row][jump_col]
                if jumped_piece != EMPTY and jumped_piece.color != piece.color:
                    # Check if landing square is empty
                    land_row, land_col = jump_row + dr, jump_col + dc
                    if 0 <= land_row < BOARD_SIZE and 0 <= land_col < BOARD_SIZE:
                        if self.board[land_row][land_col] == EMPTY:
                            jump_moves.append((land_row, land_col))
        
        return jump_moves
    
    def make_move(self, start_row, start_col, end_row, end_col):
        # Check if it's a jump move
        if abs(end_row - start_row) == 2:
            # Remove jumped piece
            jumped_row = (start_row + end_row) // 2
            jumped_col = (start_col + end_col) // 2
            self.remove_piece(jumped_row, jumped_col)
        
        self.move_piece(start_row, start_col, end_row, end_col)
    
    def get_all_pieces(self, color):
        pieces = []
        for row in range(BOARD_SIZE):
            for col in range(BOARD_SIZE):
                piece = self.board[row][col]
                if piece != EMPTY and piece.color == color:
                    pieces.append((row, col))
        return pieces
    
    def copy(self):
        new_board = Board()
        new_board.board = [[EMPTY for _ in range(BOARD_SIZE)] for _ in range(BOARD_SIZE)]
        
        for row in range(BOARD_SIZE):
            for col in range(BOARD_SIZE):
                if self.board[row][col] != EMPTY:
                    new_board.board[row][col] = self.board[row][col].copy()
        
        new_board.red_pieces = self.red_pieces
        new_board.black_pieces = self.black_pieces
        new_board.red_kings = self.red_kings
        new_board.black_kings = self.black_kings
        
        return new_board
    
    def evaluate(self):
        # Evaluation function for AI
        red_score = self.red_pieces + self.red_kings * 0.5
        black_score = self.black_pieces + self.black_kings * 0.5
        return red_score - black_score
    
    def is_game_over(self):
        if self.red_pieces == 0 or self.black_pieces == 0:
            return True
        
        # Check if any player has no valid moves
        red_has_moves = False
        black_has_moves = False
        
        for row in range(BOARD_SIZE):
            for col in range(BOARD_SIZE):
                piece = self.board[row][col]
                if piece != EMPTY:
                    moves = self.get_valid_moves(row, col)
                    if moves:
                        if piece.color == RED_PIECE:
                            red_has_moves = True
                        else:
                            black_has_moves = True
        
        return not red_has_moves or not black_has_moves
    
    def get_winner(self):
        if self.red_pieces == 0:
            return BLACK_PIECE
        elif self.black_pieces == 0:
            return RED_PIECE
        else:
            return None

class AI:
    def __init__(self, color, difficulty=2):
        self.color = color
        self.difficulty = difficulty  # 1=Easy, 2=Medium, 3=Hard
        self.difficulty_names = ["Easy", "Medium", "Hard"]
        self.max_depth = self.get_depth_for_difficulty(difficulty)
    
    def get_depth_for_difficulty(self, difficulty):
        depth_map = {1: 2, 2: 4, 3: 6}
        return depth_map.get(difficulty, 4)
    
    def set_difficulty(self, difficulty):
        self.difficulty = difficulty
        self.max_depth = self.get_depth_for_difficulty(difficulty)
    
    def minimax(self, board, depth, maximizing_player, alpha=float('-inf'), beta=float('inf')):
        if depth == 0 or board.is_game_over():
            return board.evaluate(), None
        
        if maximizing_player:
            max_eval = float('-inf')
            best_move = None
            
            for row, col in board.get_all_pieces(self.color):
                for end_row, end_col in board.get_valid_moves(row, col):
                    board_copy = board.copy()
                    board_copy.make_move(row, col, end_row, end_col)
                    
                    eval_score, _ = self.minimax(board_copy, depth - 1, False, alpha, beta)
                    
                    if eval_score > max_eval:
                        max_eval = eval_score
                        best_move = ((row, col), (end_row, end_col))
                    
                    alpha = max(alpha, eval_score)
                    if beta <= alpha:
                        break
            
            return max_eval, best_move
        else:
            min_eval = float('inf')
            best_move = None
            
            opponent_color = RED_PIECE if self.color == BLACK_PIECE else BLACK_PIECE
            
            for row, col in board.get_all_pieces(opponent_color):
                for end_row, end_col in board.get_valid_moves(row, col):
                    board_copy = board.copy()
                    board_copy.make_move(row, col, end_row, end_col)
                    
                    eval_score, _ = self.minimax(board_copy, depth - 1, True, alpha, beta)
                    
                    if eval_score < min_eval:
                        min_eval = eval_score
                        best_move = ((row, col), (end_row, end_col))
                    
                    beta = min(beta, eval_score)
                    if beta <= alpha:
                        break
            
            return min_eval, best_move
    
    def get_move(self, board):
        _, best_move = self.minimax(board, self.max_depth, True)
        return best_move

class Game:
    def __init__(self):
        self.screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
        pygame.display.set_caption("Checkers Game")
        self.clock = pygame.time.Clock()
        self.board = Board()
        self.current_player = RED_PIECE  # Human player starts
        self.selected_piece = None
        self.valid_moves = []
        self.ai = AI(BLACK_PIECE, difficulty=2)
        self.game_over = False
        self.winner = None
        self.font = pygame.font.Font(None, 36)
        self.medium_font = pygame.font.Font(None, 28)
        self.small_font = pygame.font.Font(None, 24)
        self.difficulty = 2  # Default difficulty
        self.show_game_over_menu = False
        self.sidebar_x = BOARD_SIZE * SQUARE_SIZE
        self.create_ui_elements()
    
    def create_ui_elements(self):
        # Sidebar positioning
        sidebar_center_x = self.sidebar_x + SIDEBAR_WIDTH // 2
        padding = 20
        
        # Current player section
        self.player_label_y = 30
        
        # Piece count section
        self.piece_count_y = 80
        
        # Difficulty section
        self.difficulty_label_y = 130
        self.difficulty_buttons = []
        button_width = 65
        button_height = 30
        button_spacing = 10
        
        # Calculate starting position for centered buttons (3 buttons in a row)
        total_width = 3 * button_width + 2 * button_spacing
        start_x = sidebar_center_x - total_width // 2
        
        difficulty_names = ["Easy", "Medium", "Hard"]
        for i in range(3):
            x = start_x + i * (button_width + button_spacing)
            y = self.difficulty_label_y + 30
            
            rect = pygame.Rect(x, y, button_width, button_height)
            self.difficulty_buttons.append(rect)
        
        # Action buttons
        self.restart_button_rect = pygame.Rect(sidebar_center_x - 50, 280, 100, 40)
        self.quit_button_rect = pygame.Rect(sidebar_center_x - 50, 330, 100, 40)
        
        # Instructions section
        self.instructions_y = 400
        
        # Game over menu buttons (centered on screen)
        screen_center_x = WINDOW_WIDTH // 2
        screen_center_y = WINDOW_HEIGHT // 2
        self.game_over_restart_button = pygame.Rect(screen_center_x - 100, screen_center_y + 50, 80, 40)
        self.game_over_quit_button = pygame.Rect(screen_center_x + 20, screen_center_y + 50, 80, 40)
    
    def draw_button(self, rect, text, is_active=False, font=None):
        if font is None:
            font = self.small_font
            
        # Button colors
        if is_active:
            button_color = BLUE
            text_color = WHITE
        else:
            button_color = LIGHT_GRAY
            text_color = BLACK
        
        # Draw button
        pygame.draw.rect(self.screen, button_color, rect)
        pygame.draw.rect(self.screen, BLACK, rect, 2)
        
        # Draw text
        text_surface = font.render(text, True, text_color)
        text_rect = text_surface.get_rect(center=rect.center)
        self.screen.blit(text_surface, text_rect)
    
    def draw_sidebar(self):
        # Draw sidebar background
        sidebar_rect = pygame.Rect(self.sidebar_x, 0, SIDEBAR_WIDTH, WINDOW_HEIGHT)
        pygame.draw.rect(self.screen, WHITE, sidebar_rect)
        pygame.draw.line(self.screen, BLACK, (self.sidebar_x, 0), (self.sidebar_x, WINDOW_HEIGHT), 2)
        
        sidebar_center_x = self.sidebar_x + SIDEBAR_WIDTH // 2
        
        # Game title
        title_surface = self.font.render("CHECKERS", True, BLACK)
        title_rect = title_surface.get_rect(center=(sidebar_center_x, 20))
        self.screen.blit(title_surface, title_rect)
        
        # Current player
        player_text = "Your Turn" if self.current_player == RED_PIECE else "AI Turn"
        player_color = RED if self.current_player == RED_PIECE else BLACK
        player_surface = self.medium_font.render(player_text, True, player_color)
        player_rect = player_surface.get_rect(center=(sidebar_center_x, self.player_label_y))
        self.screen.blit(player_surface, player_rect)
        
        # Piece count
        red_count_text = f"Red Pieces: {self.board.red_pieces}"
        black_count_text = f"Black Pieces: {self.board.black_pieces}"
        
        red_surface = self.small_font.render(red_count_text, True, RED)
        black_surface = self.small_font.render(black_count_text, True, BLACK)
        
        red_rect = red_surface.get_rect(center=(sidebar_center_x, self.piece_count_y))
        black_rect = black_surface.get_rect(center=(sidebar_center_x, self.piece_count_y + 25))
        
        self.screen.blit(red_surface, red_rect)
        self.screen.blit(black_surface, black_rect)
        
        # Difficulty section
        diff_label = self.medium_font.render("Difficulty", True, BLACK)
        diff_rect = diff_label.get_rect(center=(sidebar_center_x, self.difficulty_label_y))
        self.screen.blit(diff_label, diff_rect)
        
        # Difficulty buttons
        difficulty_names = ["Easy", "Medium", "Hard"]
        for i, button_rect in enumerate(self.difficulty_buttons):
            is_active = (i + 1) == self.difficulty
            self.draw_button(button_rect, difficulty_names[i], is_active)
        
        # Action buttons
        self.draw_button(self.restart_button_rect, "Restart", font=self.medium_font)
        self.draw_button(self.quit_button_rect, "Quit", font=self.medium_font)
        
        # Instructions
        instructions = [
            "Instructions:",
            "• Click pieces to select",
            "• Click highlighted spots to move",
            "• Press R to restart",
            "• Press Q/ESC to quit",
            "",
            "Red pieces are yours",
            "Black pieces are AI"
        ]
        
        for i, instruction in enumerate(instructions):
            color = BLACK if not instruction.startswith("•") else GRAY
            if instruction == "Instructions:":
                font = self.medium_font
            else:
                font = self.small_font
                
            text_surface = font.render(instruction, True, color)
            text_rect = text_surface.get_rect(center=(sidebar_center_x, self.instructions_y + i * 20))
            self.screen.blit(text_surface, text_rect)
    
    def draw_game_over_menu(self):
        # Draw semi-transparent overlay
        overlay = pygame.Surface((WINDOW_WIDTH, WINDOW_HEIGHT))
        overlay.set_alpha(128)
        overlay.fill(BLACK)
        self.screen.blit(overlay, (0, 0))
        
        screen_center_x = WINDOW_WIDTH // 2
        screen_center_y = WINDOW_HEIGHT // 2
        
        # Draw game over message
        winner_text = "You Win!" if self.winner == RED_PIECE else "AI Wins!" if self.winner == BLACK_PIECE else "Game Over!"
        winner_color = RED if self.winner == RED_PIECE else BLACK if self.winner == BLACK_PIECE else WHITE
        
        winner_surface = self.font.render(winner_text, True, winner_color)
        winner_rect = winner_surface.get_rect(center=(screen_center_x, screen_center_y - 50))
        self.screen.blit(winner_surface, winner_rect)
        
        # Draw buttons
        self.draw_button(self.game_over_restart_button, "Restart", font=self.medium_font)
        self.draw_button(self.game_over_quit_button, "Quit", font=self.medium_font)
        
        # Draw instructions
        instruction_text = "Click Restart to play again or Quit to exit"
        instruction_surface = self.small_font.render(instruction_text, True, WHITE)
        instruction_rect = instruction_surface.get_rect(center=(screen_center_x, screen_center_y + 110))
        self.screen.blit(instruction_surface, instruction_rect)
    
    def draw_board(self):
        for row in range(BOARD_SIZE):
            for col in range(BOARD_SIZE):
                color = LIGHT_BROWN if (row + col) % 2 == 0 else DARK_BROWN
                pygame.draw.rect(self.screen, color, 
                               (col * SQUARE_SIZE, row * SQUARE_SIZE, SQUARE_SIZE, SQUARE_SIZE))
    
    def draw_pieces(self):
        for row in range(BOARD_SIZE):
            for col in range(BOARD_SIZE):
                piece = self.board.get_piece(row, col)
                if piece != EMPTY:
                    center_x = col * SQUARE_SIZE + SQUARE_SIZE // 2
                    center_y = row * SQUARE_SIZE + SQUARE_SIZE // 2
                    
                    # Draw piece
                    color = RED if piece.color == RED_PIECE else BLACK
                    pygame.draw.circle(self.screen, color, (center_x, center_y), 30)
                    pygame.draw.circle(self.screen, WHITE, (center_x, center_y), 30, 3)
                    
                    # Draw king crown
                    if piece.is_king:
                        pygame.draw.circle(self.screen, (255, 215, 0), (center_x, center_y), 15)
    
    def draw_valid_moves(self):
        for row, col in self.valid_moves:
            center_x = col * SQUARE_SIZE + SQUARE_SIZE // 2
            center_y = row * SQUARE_SIZE + SQUARE_SIZE // 2
            pygame.draw.circle(self.screen, GREEN, (center_x, center_y), 10)
    
    def draw_selected_piece(self):
        if self.selected_piece:
            row, col = self.selected_piece
            pygame.draw.rect(self.screen, BLUE, 
                           (col * SQUARE_SIZE, row * SQUARE_SIZE, SQUARE_SIZE, SQUARE_SIZE), 5)
    
    def get_square_from_pos(self, pos):
        x, y = pos
        if x < BOARD_SIZE * SQUARE_SIZE and y < BOARD_SIZE * SQUARE_SIZE:
            return y // SQUARE_SIZE, x // SQUARE_SIZE
        return None, None
    
    def handle_click(self, pos):
        # Check if game over menu is showing
        if self.show_game_over_menu:
            if self.game_over_restart_button.collidepoint(pos):
                self.reset_game()
                return
            elif self.game_over_quit_button.collidepoint(pos):
                pygame.quit()
                sys.exit()
            return
        
        # Check sidebar buttons
        if self.restart_button_rect.collidepoint(pos):
            self.reset_game()
            return
        elif self.quit_button_rect.collidepoint(pos):
            pygame.quit()
            sys.exit()
        
        # Check difficulty buttons
        for i, button_rect in enumerate(self.difficulty_buttons):
            if button_rect.collidepoint(pos):
                self.difficulty = i + 1
                self.ai.set_difficulty(self.difficulty)
                return
        
        # Game logic only if not game over and on board
        if self.game_over or self.current_player != RED_PIECE:
            return
        
        row, col = self.get_square_from_pos(pos)
        if row is None:
            return
        
        if self.selected_piece is None:
            # Select a piece
            piece = self.board.get_piece(row, col)
            if piece != EMPTY and piece.color == RED_PIECE:
                self.selected_piece = (row, col)
                self.valid_moves = self.board.get_valid_moves(row, col)
        else:
            # Try to move the selected piece
            if (row, col) in self.valid_moves:
                start_row, start_col = self.selected_piece
                self.board.make_move(start_row, start_col, row, col)
                self.current_player = BLACK_PIECE
                self.selected_piece = None
                self.valid_moves = []
                
                # Check for game over
                if self.board.is_game_over():
                    self.game_over = True
                    self.winner = self.board.get_winner()
                    self.show_game_over_menu = True
            else:
                # Deselect or select a different piece
                piece = self.board.get_piece(row, col)
                if piece != EMPTY and piece.color == RED_PIECE:
                    self.selected_piece = (row, col)
                    self.valid_moves = self.board.get_valid_moves(row, col)
                else:
                    self.selected_piece = None
                    self.valid_moves = []
    
    def handle_keypress(self, event):
        if event.key == pygame.K_1:
            self.difficulty = 1
            self.ai.set_difficulty(1)
        elif event.key == pygame.K_2:
            self.difficulty = 2
            self.ai.set_difficulty(2)
        elif event.key == pygame.K_3:
            self.difficulty = 3
            self.ai.set_difficulty(3)
        elif event.key == pygame.K_r:
            self.reset_game()
        elif event.key == pygame.K_q or event.key == pygame.K_ESCAPE:
            pygame.quit()
            sys.exit()
    
    def reset_game(self):
        self.board = Board()
        self.current_player = RED_PIECE
        self.selected_piece = None
        self.valid_moves = []
        self.game_over = False
        self.winner = None
        self.show_game_over_menu = False
    
    def ai_move(self):
        if self.current_player == BLACK_PIECE and not self.game_over:
            move = self.ai.get_move(self.board)
            if move:
                (start_row, start_col), (end_row, end_col) = move
                self.board.make_move(start_row, start_col, end_row, end_col)
                self.current_player = RED_PIECE
                
                # Check for game over
                if self.board.is_game_over():
                    self.game_over = True
                    self.winner = self.board.get_winner()
                    self.show_game_over_menu = True
    
    def run(self):
        running = True
        
        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    self.handle_click(event.pos)
                elif event.type == pygame.KEYDOWN:
                    self.handle_keypress(event)
            
            # AI move
            if self.current_player == BLACK_PIECE and not self.game_over:
                self.ai_move()
            
            # Draw everything
            self.screen.fill(LIGHT_GRAY)
            self.draw_board()
            self.draw_pieces()
            self.draw_selected_piece()
            self.draw_valid_moves()
            self.draw_sidebar()
            
            # Draw game over menu if needed
            if self.show_game_over_menu:
                self.draw_game_over_menu()
            
            pygame.display.flip()
            self.clock.tick(FPS)
        
        pygame.quit()
        sys.exit()

if __name__ == "__main__":
    game = Game()
    game.run()