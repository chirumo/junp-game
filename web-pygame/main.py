import asyncio  # これが必須の奴
import pygame
import random
import math
import sys

# 初期化
pygame.init()
width, height = 900, 600
screen = pygame.display.set_mode((width, height))
pygame.display.set_caption("Falling Balls Game")
clock = pygame.time.Clock()


# 物理演算用のクラス
class Ball:
    def __init__(self, x, y, radius, size_label):
        self.x = x
        self.y = y
        self.vx = 0
        self.vy = 0
        self.radius = radius
        self.size_label = size_label
        self.color = self.get_color(size_label)
        self.angle = 0
        self.angular_velocity = 0

    def get_color(self, size_label):
        colors = [
            (255, 100, 100),
            (100, 255, 100),
            (100, 100, 255),
            (255, 255, 100),
            (255, 100, 255),
            (100, 255, 255),
            (255, 200, 100),
            (200, 100, 255),
            (100, 200, 255),
            (255, 150, 150),
        ]
        return colors[(size_label - 1) % len(colors)]

    def update(self, dt):
        # 重力を適用
        self.vy += 1600 * dt  # 重力加速度

        # 位置を更新
        self.x += self.vx * dt
        self.y += self.vy * dt

        # 角度を更新
        self.angle += self.angular_velocity * dt

        # 壁との衝突判定
        if self.x - self.radius <= 195:
            self.x = 195 + self.radius
            self.vx = -self.vx * 0.8
            self.angular_velocity = -self.vx / self.radius
        elif self.x + self.radius >= width - 195:
            self.x = width - 195 - self.radius
            self.vx = -self.vx * 0.8
            self.angular_velocity = -self.vx / self.radius

        # 床との衝突判定
        if self.y + self.radius >= height - 50:
            self.y = height - 50 - self.radius
            self.vy = -self.vy * 0.8
            self.vx *= 0.9  # 摩擦
            if abs(self.vy) < 10:
                self.vy = 0
            if abs(self.vx) < 5:
                self.vx = 0
                self.angular_velocity = 0

    def draw(self, screen):
        # ボールを描画
        pygame.draw.circle(screen, self.color, (int(self.x), int(self.y)), self.radius)
        pygame.draw.circle(
            screen, (255, 255, 255), (int(self.x), int(self.y)), self.radius, 2
        )

        # サイズラベルを描画
        font = pygame.font.SysFont("Arial", int(self.radius // 2))
        text = font.render(str(self.size_label), True, (255, 255, 255))
        text_rect = text.get_rect(center=(int(self.x), int(self.y)))
        screen.blit(text, text_rect)


def check_collision(ball1, ball2):
    dx = ball1.x - ball2.x
    dy = ball1.y - ball2.y
    distance = math.sqrt(dx * dx + dy * dy)
    return distance < (ball1.radius + ball2.radius)


def resolve_collision(ball1, ball2):
    dx = ball1.x - ball2.x
    dy = ball1.y - ball2.y
    distance = math.sqrt(dx * dx + dy * dy)

    if distance == 0:
        return

    # 正規化されたベクトル
    nx = dx / distance
    ny = dy / distance

    # 重なりを解決
    overlap = ball1.radius + ball2.radius - distance
    ball1.x += nx * overlap * 0.5
    ball1.y += ny * overlap * 0.5
    ball2.x -= nx * overlap * 0.5
    ball2.y -= ny * overlap * 0.5

    # 相対速度
    dvx = ball1.vx - ball2.vx
    dvy = ball1.vy - ball2.vy

    # 相対速度の法線成分
    dvn = dvx * nx + dvy * ny

    # 衝突しない場合
    if dvn > 0:
        return

    # 反発係数
    e = 0.8

    # 衝突後の速度
    impulse = 2 * dvn / 2  # 質量を同じと仮定
    ball1.vx -= impulse * nx
    ball1.vy -= impulse * ny
    ball2.vx += impulse * nx
    ball2.vy += impulse * ny


# 背景画像を作成（グラデーション）
def create_background():
    background = pygame.Surface((width, height))
    for y in range(height):
        color_ratio = y / height
        r = int(135 + (176 - 135) * color_ratio)
        g = int(206 + (224 - 206) * color_ratio)
        b = int(235 + (230 - 235) * color_ratio)
        pygame.draw.line(background, (r, g, b), (0, y), (width, y))
    return background


background_image = create_background()


# ゲーム状態の初期化
def initialize_game():
    global game_over, start_ticks, score, next_ball_type, balls

    game_over = False
    start_ticks = pygame.time.get_ticks()
    score = 0
    next_ball_type = 1
    balls = []


# 制限時間（秒）
time_limit = 10000000


def create_ball(x, y, update_next, radius=None):
    global next_ball_type
    if radius is None:
        radius = next_ball_type * 10
    size_label = radius // 10
    ball = Ball(x, y, radius, size_label)
    balls.append(ball)

    if update_next:
        next_ball_type = random.choice([i for i in range(1, 6)])


def merge_balls(ball1, ball2):
    global score

    # 一番大きいサイズのボールのサイズラベルは10
    if ball1.size_label == 10 and ball2.size_label == 10:
        balls.remove(ball1)
        balls.remove(ball2)
        score += ball1.size_label
        return

    if ball1.size_label == ball2.size_label and ball1.size_label < 10:
        new_radius = ball1.radius + 10
        mid_x = (ball1.x + ball2.x) / 2
        mid_y = (ball1.y + ball2.y) / 2
        create_ball(mid_x, mid_y, False, new_radius)
        balls.remove(ball1)
        balls.remove(ball2)
        score += ball1.size_label


# 既存のボールとの重複をチェックする関数
def is_overlapping_with_existing_balls(x, y, radius):
    for ball in balls:
        distance = math.sqrt((x - ball.x) ** 2 + (y - ball.y) ** 2)
        if distance < radius + ball.radius:
            return True
    return False


# 再挑戦ボタンの描画と判定
def draw_retry_button():
    button_width, button_height = 200, 60
    button_x = width // 2 - button_width // 2
    button_y = height // 2 + 100

    # ボタンの背景
    pygame.draw.rect(
        screen, (80, 80, 80), (button_x, button_y, button_width, button_height)
    )
    pygame.draw.rect(
        screen, (255, 255, 255), (button_x, button_y, button_width, button_height), 3
    )

    # ボタンのテキスト
    font = pygame.font.SysFont("Arial", 36)
    retry_text = font.render("RETRY", True, (255, 255, 255))
    text_rect = retry_text.get_rect(
        center=(button_x + button_width // 2, button_y + button_height // 2)
    )
    screen.blit(retry_text, text_rect)

    return pygame.Rect(button_x, button_y, button_width, button_height)


async def main():  # これが必須の奴
    global game_over, start_ticks, score, next_ball_type, balls

    # ゲームを初期化
    initialize_game()

    running = True
    last_time = pygame.time.get_ticks()

    # 次のボール表示用の色
    next_ball_colors = [
        (255, 100, 100),
        (100, 255, 100),
        (100, 100, 255),
        (255, 255, 100),
        (255, 100, 255),
    ]

    while running:
        current_time = pygame.time.get_ticks()
        dt = (current_time - last_time) / 1000.0
        last_time = current_time

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.MOUSEBUTTONDOWN:
                if game_over:
                    # ゲームオーバー時の再挑戦ボタンクリック判定
                    retry_button_rect = pygame.Rect(
                        width // 2 - 100, height // 2 + 100, 200, 60
                    )
                    if retry_button_rect.collidepoint(event.pos):
                        initialize_game()  # ゲームをリセット
                else:
                    # 通常のゲームプレイ時のボール配置
                    if event.pos[1] < 120:  # 画面の上部120px内の場合
                        if not is_overlapping_with_existing_balls(
                            event.pos[0], event.pos[1], next_ball_type * 10
                        ):
                            create_ball(event.pos[0], event.pos[1], True)

        screen.blit(background_image, (0, 0))

        if not game_over:
            # ボールの更新
            for ball in balls:
                ball.update(dt)

            # ボール同士の衝突判定
            balls_to_merge = []
            for i in range(len(balls)):
                for j in range(i + 1, len(balls)):
                    ball1, ball2 = balls[i], balls[j]
                    if check_collision(ball1, ball2):
                        if ball1.size_label == ball2.size_label:
                            balls_to_merge.append((ball1, ball2))
                        else:
                            resolve_collision(ball1, ball2)

            # マージ処理
            for ball1, ball2 in balls_to_merge:
                if ball1 in balls and ball2 in balls:
                    merge_balls(ball1, ball2)

            # ボールの描画
            for ball in balls:
                ball.draw(screen)

            # ゲームオーバー判定
            for ball in balls:
                if ball.y - ball.radius < 97:  # 上部の境界線
                    game_over = True

            # 壁と床の描画
            pygame.draw.line(
                screen, (100, 20, 0), (195, 97), (195, height - 50), 20
            )  # 左の壁
            pygame.draw.line(
                screen, (100, 20, 0), (width - 195, 97), (width - 195, height - 50), 20
            )  # 右の壁
            pygame.draw.line(
                screen, (100, 20, 0), (195, height - 50), (width - 195, height - 50), 20
            )  # 床

            # 角の丸み
            pygame.draw.circle(screen, (100, 20, 0), (195, height - 50), 10)
            pygame.draw.circle(screen, (100, 20, 0), (width - 195, height - 50), 10)
            pygame.draw.circle(screen, (95, 5, 0), (195, 97), 10)
            pygame.draw.circle(screen, (95, 5, 0), (width - 195, 97), 10)

            # 経過時間の計算（秒）
            seconds = (pygame.time.get_ticks() - start_ticks) // 1000

            # 画面の上部に暗い矩形を描画
            dark_surface = pygame.Surface((width, 75), pygame.SRCALPHA)
            dark_surface.fill((0, 0, 0, 128))
            screen.blit(dark_surface, (0, 0))

            # 次のボールを表示
            next_ball_radius = next_ball_type * 10
            next_ball_color = next_ball_colors[
                (next_ball_type - 1) % len(next_ball_colors)
            ]
            pygame.draw.circle(
                screen, next_ball_color, (width - 90, 37), next_ball_radius
            )
            pygame.draw.circle(
                screen, (255, 255, 255), (width - 90, 37), next_ball_radius, 2
            )

            # 画面の指定された位置にスコアを表示
            font = pygame.font.SysFont("Arial", 36)
            score_text = font.render(f"SCORE: {score}", True, (255, 255, 255))
            screen.blit(score_text, (50, 25))

            screen.blit(font.render("NEXT: ", True, (255, 255, 255)), (width - 168, 10))

            text = font.render(f"Time: {time_limit - seconds}", True, (255, 255, 255))
            screen.blit(text, (width - 200, 50))

            if seconds >= 1000:
                game_over = True

        if game_over:
            # 半透明の黒で画面を暗くします
            overlay = pygame.Surface((width, height))
            overlay.set_alpha(180)
            overlay.fill((0, 0, 0))
            screen.blit(overlay, (0, 0))

            font = pygame.font.SysFont("Arial", 54)
            gameover_text = font.render("Game Over", True, (255, 255, 255))
            gameover_pos = gameover_text.get_rect(center=(width / 2, height / 2 - 40))
            screen.blit(gameover_text, gameover_pos)

            score_text = font.render(f"Score: {score}", True, (255, 255, 255))
            score_pos = score_text.get_rect(center=(width / 2, height / 2 + 40))
            screen.blit(score_text, score_pos)

            # 再挑戦ボタンを描画
            draw_retry_button()

        pygame.display.flip()
        clock.tick(60)
        await asyncio.sleep(0)  # これが必須の奴


asyncio.run(main())  # これが必須の奴
