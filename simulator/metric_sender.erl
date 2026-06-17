-module(metric_sender).

-export([
    hello/0,
    start/0,
    start_nodes/0,
    send_once/2,
    send_forever/2,
    metric_body/2,
    build_body/5
]).

hello() ->
    io:format("Erlang simulator is working~n").

start() ->
    start_nodes(),
    keep_alive().

keep_alive() ->
    timer:sleep(1000000),
    keep_alive().

start_nodes() ->
    spawn(fun() -> send_forever("erlang_node_001", stable) end),
    spawn(fun() -> send_forever("erlang_node_002", unstable) end),
    spawn(fun() -> send_forever("erlang_node_003", critical) end),
    io:format("Started simulated Erlang nodes~n").

send_forever(NodeId, Profile) ->
    send_once(NodeId, Profile),
    timer:sleep(5000),
    send_forever(NodeId, Profile).

send_once(NodeId, Profile) ->
    application:ensure_all_started(inets),

    Url = "http://127.0.0.1:8000/metrics",

    Body = lists:flatten(metric_body(NodeId, Profile)),

    Headers = [],
    ContentType = "application/json",

    Request = {Url, Headers, ContentType, Body},

    case httpc:request(post, Request, [], []) of
        {ok, {{_, StatusCode, _}, _ResponseHeaders, ResponseBody}} ->
            io:format("Node ~s sent metric. Status code: ~p~n", [NodeId, StatusCode]),
            io:format("Response: ~s~n", [ResponseBody]);

        {error, Reason} ->
            io:format("Node ~s request failed: ~p~n", [NodeId, Reason])
    end.

metric_body(NodeId, stable) ->
    Chance = rand:uniform(100),

    case Chance =< 15 of
        true ->
            alert_body(NodeId);
        false ->
            healthy_body(NodeId)
    end;

metric_body(NodeId, unstable) ->
    Chance = rand:uniform(100),

    case Chance =< 50 of
        true ->
            alert_body(NodeId);
        false ->
            healthy_body(NodeId)
    end;

metric_body(NodeId, critical) ->
    Chance = rand:uniform(100),

    case Chance =< 80 of
        true ->
            alert_body(NodeId);
        false ->
            healthy_body(NodeId)
    end.

healthy_body(NodeId) ->
    build_body(
        NodeId,
        rand:uniform(120),
        rand:uniform(3),
        rand:uniform(60),
        rand:uniform(60)
    ).

alert_body(NodeId) ->
    AlertType = rand:uniform(4),

    case AlertType of
        1 ->
            high_latency_body(NodeId);
        2 ->
            packet_loss_body(NodeId);
        3 ->
            high_cpu_body(NodeId);
        4 ->
            high_memory_body(NodeId)
    end.

high_latency_body(NodeId) ->
    build_body(
        NodeId,
        200 + rand:uniform(150),
        rand:uniform(3),
        rand:uniform(60),
        rand:uniform(60)
    ).

packet_loss_body(NodeId) ->
    build_body(
        NodeId,
        rand:uniform(120),
        5 + rand:uniform(10),
        rand:uniform(60),
        rand:uniform(60)
    ).

high_cpu_body(NodeId) ->
    build_body(
        NodeId,
        rand:uniform(120),
        rand:uniform(3),
        90 + rand:uniform(10),
        rand:uniform(60)
    ).

high_memory_body(NodeId) ->
    build_body(
        NodeId,
        rand:uniform(120),
        rand:uniform(3),
        rand:uniform(60),
        90 + rand:uniform(10)
    ).

build_body(NodeId, Latency, PacketLoss, CpuUsage, MemoryUsage) ->
    io_lib:format(
        "{
            \"node_id\": \"~s\",
            \"latency_ms\": ~p,
            \"packet_loss\": ~p,
            \"cpu_usage\": ~p,
            \"memory_usage\": ~p
        }",
        [NodeId, Latency, PacketLoss, CpuUsage, MemoryUsage]
    ).