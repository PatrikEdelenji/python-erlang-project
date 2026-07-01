-module(network_node).

-export([start_link/3]).

start_link(NodeId, Profile, CrashChance) ->
    Pid = spawn_link(fun() -> init(NodeId, Profile, CrashChance) end),
    {ok, Pid}.

init(NodeId, Profile, CrashChance) ->
    io:format(
        "Starting node ~s with profile ~p, crash chance ~p%, pid ~p~n",
        [NodeId, Profile, CrashChance, self()]
    ),
    loop(NodeId, Profile, CrashChance).

loop(NodeId, Profile, CrashChance) ->
    maybe_crash(NodeId, CrashChance),
    metric_sender:send_once(NodeId, Profile),
    timer:sleep(5000),
    loop(NodeId, Profile, CrashChance).

maybe_crash(_NodeId, 0) ->
    ok;

maybe_crash(NodeId, CrashChance) ->
    Chance = rand:uniform(100),

    case Chance =< CrashChance of
        true ->
            io:format("Node ~s crashed with configured chance ~p%~n", [NodeId, CrashChance]),
            exit(simulated_crash);
        false ->
            ok
    end.