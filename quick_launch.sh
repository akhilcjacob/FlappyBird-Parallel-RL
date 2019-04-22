echo "Launching 1 agent..."
nohup python flappy.py 1 > output/1_agent & 
sleep 4s

echo "Launching 4 agents..."
nohup python flappy.py 4 > output/4_agent & 
sleep 4s

echo "Launching 8 agents..."
nohup python flappy.py 8 > output/8_agent & 
sleep 4s

echo "Launching 20 agents..."
nohup python flappy.py 20 > output/20_agent &
sleep 4s

echo "Launching kill 2h kill command..."
sleep 120m && pkill -9 python &
echo "Done..."