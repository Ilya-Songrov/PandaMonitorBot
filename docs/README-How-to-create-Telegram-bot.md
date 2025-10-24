

## Як створити Telegram бота

1. **Створіть бота через BotFather:**
   - Відкрийте Telegram і знайдіть [@BotFather](https://t.me/BotFather)
   - Відправте команду `/newbot`
   - Оберіть ім'я для вашого бота (наприклад: "My Monitor Bot")
   - Оберіть username для бота (наприклад: "my_monitor_bot")
   - BotFather надасть вам **токен бота** - збережіть його!

2. **Отримайте ваш User ID:**
   - Знайдіть [@userinfobot](https://t.me/userinfobot) в Telegram
   - Відправте команду `/start`
   - Бот покаже ваш **User ID** - збережіть його!

3. **Налаштуйте змінні середовища:**
   ```bash
   # Скопіюйте файл прикладу
   cp .env.example .env

   # Відредагуйте .env файл
   nano .env
   ```
   
   Заповніть наступні поля в `.env`:
   ```bash
   BOT_TOKEN=token_from_BotFather
   ALLOWED_USER_IDS=your_user_id,other_user_id
   COMPUTER_NAME=MyComputer
   MONITOR_INTERVAL=60
   ```
