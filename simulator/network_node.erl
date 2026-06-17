-module(network_node).

-export([start_link/2]).

start_link(NodeId, Profile) ->
    Pid = spawn_link(fun() -> init(NodeId, Profile) end),
    {ok, Pid}.

init(NodeId, Profile) ->
    io:format("Starting node ~s with profile ~p~n", [NodeId, Profile]),
    loop(NodeId, Profile).

loop(NodeId, Profile) ->
    maybe_crash(NodeId, Profile),
    metric_sender:send_once(NodeId, Profile),
    timer:sleep(5000),
    loop(NodeId, Profile).

maybe_crash(NodeId, critical) ->
    Chance = rand:uniform(100),

    case Chance =< 10 of
        true ->
            io:format("Node ~s crashed due to critical state~n", [NodeId]),
            exit(simulated_crash);
        false ->
            ok
    end;

maybe_crash(_NodeId, _Profile) ->
    ok.