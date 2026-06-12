-module(metric_sender).
-export([hello/0, send_once/1, random_metric_body/1, send_loop/2]).

hello() ->
    io:format("Erlang simulator is working~n").

send_once(NodeId) ->
    application:ensure_all_started(inets),

    Url = "http://127.0.0.1:8000/metrics",

    Body = lists:flatten(random_metric_body(NodeId)),

    Headers = [],
    ContentType = "application/json",

    Request = {Url, Headers, ContentType, Body},

    case httpc:request(post, Request, [], []) of
        {ok, {{_, StatusCode, _}, _ResponseHeaders, ResponseBody}} ->
            io:format("Status code: ~p~n", [StatusCode]),
            io:format("Response: ~s~n", [ResponseBody]);

        {error, Reason} ->
            io:format("Request failed: ~p~n", [Reason])
    end.


random_metric_body(NodeId) ->
    Latency = rand:uniform(300),
    PacketLoss = rand:uniform(10),
    CpuUsage = rand:uniform(100),
    MemoryUsage = rand:uniform(100),

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


send_loop(_NodeId, 0) ->
    io:format("Finished sending metrics~n");

send_loop(NodeId, Count) ->
    send_once(NodeId),
    timer:sleep(3000),
    send_loop(NodeId, Count - 1).