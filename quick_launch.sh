python flappy.py 1 > output/1_agent & disown
sleep 4s

python flappy.py 4 > output/4_agent & disown
sleep 4s

python flappy.py 8 > output/8_agent & disown
sleep 4s

python flappy.py 20 > output/20_agent & disown
sleep 4s

sleep 120m && pkill -9 python