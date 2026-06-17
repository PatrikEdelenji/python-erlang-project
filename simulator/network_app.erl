-module(network_app).

-export([start/0]).

start() ->
    network_sup:start_link(),
    keep_alive().

keep_alive() ->
    timer:sleep(1000000),
    keep_alive().