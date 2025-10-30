

## 🚀 Deploy on Server
```bash
# clone
GIT_TOKEN='<token>'
BOT_TOKEN='<token>'
ALLOWED_USER_IDS='<ids>'
DIR_SRC='<path>'
DIR_WORKING='<path>'

mkdir -p $DIR_SRC
mkdir -p $DIR_WORKING
cd $DIR_SRC
git clone https://oauth2:$GIT_TOKEN@github.com/Ilya-Songrov/PandaMonitorBot.git
cd $DIR_SRC/PandaMonitorBot
git checkout master
cp .env.example .env
echo '
DEPLOY_ROOT_DIR='$DIR_WORKING'
BOT_TOKEN='$BOT_TOKEN'
ALLOWED_USER_IDS='$ALLOWED_USER_IDS'
' >> .env
./build-and-run-bot.sh
```