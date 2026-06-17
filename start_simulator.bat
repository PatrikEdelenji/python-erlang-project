@echo off

echo Starting Erlang network simulator...
cd simulator
erlc metric_sender.erl
erlc network_node.erl
erlc network_sup.erl
erlc network_app.erl
erl -noshell -s network_app start