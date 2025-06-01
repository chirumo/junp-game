#
# まえのやつ
#

# import pygame
# import pymunk
# import random
# import math

# # 初期化
# pygame.init()
# width, height = 900, 600
# screen = pygame.display.set_mode((width, height))
# pygame.display.set_caption("Falling Balls Game")
# clock = pygame.time.Clock()
# background_image = pygame.image.load("../images/bg.png")
# background_image = pygame.transform.scale(
#     background_image, (width, height)
# )  # 画面サイズに合わせてスケーリング

# ball_spawn_sound = pygame.mixer.Sound("../sounds/Motion-Pop08-1.mp3")
# ball_merge_sound = pygame.mixer.Sound("../sounds/Motion-Pop03-1.mp3")
# # ball_merge_sound = pygame.mixer.Sound("../sounds/Motion-Pop08-8L.mp3")


# # ゲーム状態の初期化
# def initialize_game():
#     global game_over, start_ticks, walls, score, next_ball_type, space, balls, floor

#     game_over = False
#     start_ticks = pygame.time.get_ticks()
#     walls = []
#     score = 0
#     next_ball_type = 1
#     balls = []

#     # Pymunkのスペースを設定
#     space = pymunk.Space()
#     space.gravity = (0, 1000)

#     # 床を設定
#     floor = pymunk.Segment(
#         space.static_body, (195, height - 50), (width - 195, height - 50), 20
#     )
#     floor.friction = 0.8
#     floor.elasticity = 0.8
#     space.add(floor)

#     # 壁を作成
#     create_walls(space)

#     # 衝突ハンドラーを設定
#     collision_handler = space.add_collision_handler(1, 1)
#     collision_handler.begin = merge_balls


# # 制限時間（秒）
# time_limit = 10000000

# # ゲームの初期化部分の直後に追加
# ball_images = {}
# for i in range(1, 11):
#     image = pygame.image.load(f"../images/ball_{i}.png")
#     ball_images[i] = pygame.transform.smoothscale(
#         image, (i * 30, i * 30)
#     )  # 2倍のサイズになるようにスケーリング


# def create_ball(x, y, update_next, radius=None):
#     global next_ball_type
#     if radius is None:
#         radius = next_ball_type * 10
#     mass = 1
#     moment = pymunk.moment_for_circle(mass, 0, radius)
#     body = pymunk.Body(mass, moment)
#     body.position = x, y
#     shape = pymunk.Circle(body, radius)
#     shape.friction = 0.7
#     shape.elasticity = 0.8
#     shape.size_label = radius // 10  # このラベルでサイズを識別
#     shape.image = ball_images[shape.size_label]
#     space.add(body, shape)
#     balls.append(shape)
#     shape.collision_type = 1  # すべてのボールに同じcollision_typeを設定
#     ball_spawn_sound.play()
#     if update_next:
#         next_ball_type = random.choice([i for i in range(1, 6)])


# def merge_balls(arbiter, space, _):
#     global next_ball_type, score  # scoreをglobal変数として参照
#     ball1, ball2 = arbiter.shapes

#     # 一番大きいサイズのボールのサイズラベルは10
#     if ball1.size_label == 10 and ball2.size_label == 10:
#         balls.remove(ball1)
#         balls.remove(ball2)
#         space.remove(ball1, ball1.body, ball2, ball2.body)
#         ball_merge_sound.play()
#         score += ball1.size_label
#         return False  # この衝突は他の処理を行わない

#     if ball1.size_label == ball2.size_label:
#         new_radius = ball1.radius + 10
#         mid_x = (ball1.body.position.x + ball2.body.position.x) / 2
#         mid_y = (ball1.body.position.y + ball2.body.position.y) / 2
#         create_ball(mid_x, mid_y, False, new_radius)
#         balls.remove(ball1)
#         balls.remove(ball2)
#         space.remove(ball1, ball1.body, ball2, ball2.body)
#         ball_merge_sound.play()
#         score += ball1.size_label
#     return True


# def create_walls(space):
#     thickness = 20
#     global walls
#     walls = [
#         pymunk.Segment(
#             space.static_body, (195, 97), (195, height - 50), thickness
#         ),  # 左の壁
#         pymunk.Segment(
#             space.static_body, (width - 195, 97), (width - 195, height - 50), thickness
#         ),  # 右の壁
#     ]
#     for wall in walls:
#         wall.friction = 1.0
#         wall.elasticity = 0.95
#         wall.color = pygame.Color("black")
#     space.add(*walls)


# def to_pygame(p):
#     """Convert pymunk to pygame coordinates"""
#     return int(p.x), int(-p.y + height)


# # 既存のボールとの重複をチェックする関数
# def is_overlapping_with_existing_balls(x, y, radius):
#     for ball in balls:
#         distance = (
#             (x - ball.body.position.x) ** 2 + (y - ball.body.position.y) ** 2
#         ) ** 0.5
#         if distance < radius:  # 2つのボールの半径の合計よりも距離が小さい場合
#             return True
#     return False


# # 再挑戦ボタンの描画と判定
# def draw_retry_button():
#     button_width, button_height = 200, 60
#     button_x = width // 2 - button_width // 2
#     button_y = height // 2 + 100

#     # ボタンの背景
#     pygame.draw.rect(
#         screen, (80, 80, 80), (button_x, button_y, button_width, button_height)
#     )
#     pygame.draw.rect(
#         screen, (255, 255, 255), (button_x, button_y, button_width, button_height), 3
#     )

#     # ボタンのテキスト
#     font = pygame.font.Font("../BitCheese10(sRB).TTF", 36)
#     retry_text = font.render("RETRY", True, (255, 255, 255))
#     text_rect = retry_text.get_rect(
#         center=(button_x + button_width // 2, button_y + button_height // 2)
#     )
#     screen.blit(retry_text, text_rect)

#     return pygame.Rect(button_x, button_y, button_width, button_height)


# # ゲームを初期化
# initialize_game()

# running = True
# while running:
#     for event in pygame.event.get():
#         if event.type == pygame.QUIT:
#             running = False
#         if event.type == pygame.MOUSEBUTTONDOWN:
#             if game_over:
#                 # ゲームオーバー時の再挑戦ボタンクリック判定
#                 retry_button_rect = pygame.Rect(
#                     width // 2 - 100, height // 2 + 100, 200, 60
#                 )
#                 if retry_button_rect.collidepoint(event.pos):
#                     initialize_game()  # ゲームをリセット
#             else:
#                 # 通常のゲームプレイ時のボール配置
#                 if event.pos[1] < 120:  # 画面の上部120px内の場合
#                     if not is_overlapping_with_existing_balls(
#                         event.pos[0], event.pos[1], next_ball_type * 10
#                     ):
#                         create_ball(event.pos[0], event.pos[1], True)

#     screen.blit(background_image, (0, 0))

#     if not game_over:
#         balls_to_remove = []
#         for ball in balls:
#             image = ball.image
#             angle_degrees = -math.degrees(
#                 ball.body.angle
#             )  # ボールの角度を取得し、ラジアンから度に変換
#             rotated_image = pygame.transform.rotate(
#                 ball.image, angle_degrees
#             )  # 画像を回転させる

#             # 画像の新しい中心位置を取得
#             x, y = int(ball.body.position.x), int(ball.body.position.y)
#             rect = rotated_image.get_rect(center=(x, y))

#             # 回転した画像を描画
#             screen.blit(rotated_image, rect.topleft)

#         for ball in balls:
#             if ball.body.position.y + ball.radius > height:
#                 game_over = True

#         for ball in balls_to_remove:
#             space.remove(ball, ball.body)
#             balls.remove(ball)

#         for wall in walls:
#             p1 = int(wall.a[0]), int(wall.a[1])
#             p2 = int(wall.b[0]), int(wall.b[1])
#             pygame.draw.line(screen, (100, 20, 0), p1, p2, int(wall.radius))

#         # 経過時間の計算（秒）
#         seconds = (pygame.time.get_ticks() - start_ticks) // 1000

#         space.step(1 / 60.0)

#         thickness = 10
#         corner_radius = thickness
#         pygame.draw.line(
#             screen, (100, 20, 0), (195, height - 50), (width - 195, height - 50), 20
#         )
#         pygame.draw.circle(screen, (100, 20, 0), (196, height - 50), corner_radius)
#         pygame.draw.circle(
#             screen, (100, 20, 0), (width - 194, height - 50), corner_radius
#         )
#         pygame.draw.circle(screen, (95, 5, 0), (196, 97), corner_radius)
#         pygame.draw.circle(screen, (95, 5, 0), (width - 194, 97), corner_radius)

#         # 画面の上100pxの部分に暗い矩形を描画
#         dark_surface = pygame.Surface(
#             (width, 75), pygame.SRCALPHA
#         )  # 半透明のサーフェスを作成
#         dark_surface.fill((0, 0, 0, 128))  # RGBAで黒色の半透明の色を設定
#         screen.blit(dark_surface, (0, 0))  # サーフェスを画面に描画

#         next_ball_image = ball_images[next_ball_type]
#         next_ball_center_pos = (
#             width - 90 - next_ball_image.get_width() // 2,
#             197 - next_ball_image.get_height() // 2,
#         )
#         screen.blit(next_ball_image, next_ball_center_pos)

#         # 画面の指定された位置にスコアを表示
#         font = pygame.font.Font("../BitCheese10(sRB).TTF", 36)
#         score_text = font.render(f"SCORE: {score}", True, (255, 255, 255))
#         score_position = (50, 25)  # 「2」の位置
#         screen.blit(score_text, score_position)

#         screen.blit(font.render("NEXT: ", True, (255, 255, 255)), (width - 168, 98))

#         text = font.render(f"Time: {time_limit - seconds}", True, (255, 255, 255))
#         screen.blit(text, (width - 200, 25))
#         if seconds == 1000:
#             game_over = True

#     if game_over:
#         # 半透明の黒で画面を暗くします
#         overlay = pygame.Surface((width, height))
#         overlay.set_alpha(180)
#         overlay.fill((0, 0, 0))
#         screen.blit(overlay, (0, 0))

#         font = pygame.font.Font("../BitCheese10(sRB).TTF", 54)
#         gameover_text = font.render("Game Over", 1, (255, 255, 255))
#         gameover_pos = gameover_text.get_rect(center=(width / 2, height / 2 - 40))
#         screen.blit(gameover_text, gameover_pos)

#         score_text = font.render(f"Score: {score}", 1, (255, 255, 255))
#         score_pos = score_text.get_rect(center=(width / 2, height / 2 + 40))
#         screen.blit(score_text, score_pos)

#         # 再挑戦ボタンを描画
#         draw_retry_button()

#     pygame.display.flip()
#     clock.tick(60)

# pygame.quit()
