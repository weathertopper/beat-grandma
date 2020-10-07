
if [ -z "$1" ]
  then
    echo "Pass in GAME_MODE"
    exit
fi
GAME_MODE=$1

if [ -z "$2" ]
  then
    echo "Pass in GAME_NAME"
    exit
fi
GAME_NAME=$2

ALIAS="alias 'bg=python ./beat-grandma.py -g $GAME_NAME"

if [ $GAME_MODE == "solo" ]; then
  ALIAS="$ALIAS -m solo"
fi

ALIAS="$ALIAS'"

echo
echo "RUN THE FOLLOWING FOR EASIER GAMEPLAY:"
echo
echo $ALIAS
echo