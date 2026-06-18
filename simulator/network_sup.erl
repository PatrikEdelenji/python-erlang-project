-module(network_sup).

-behaviour(supervisor).

-export([start_link/0]).
-export([init/1]).

start_link() ->
    supervisor:start_link({local, ?MODULE}, ?MODULE, []).

init([]) ->
    Nodes = load_nodes(),
    Children = build_children(Nodes),

    SupFlags = #{
        strategy => one_for_one,
        intensity => 5,
        period => 10
    },

    {ok, {SupFlags, Children}}.

load_nodes() ->
    case file:consult("nodes.config") of
        {ok, [Nodes]} ->
            Nodes;

        {error, Reason} ->
            io:format("Failed to load nodes.config: ~p~n", [Reason]),
            []
    end.

build_children(Nodes) ->
    lists:map(
        fun({NodeId, Profile, CrashChance}) ->
            #{
                id => list_to_atom(NodeId),
                start => {network_node, start_link, [NodeId, Profile, CrashChance]},
                restart => permanent,
                shutdown => 5000,
                type => worker,
                modules => [network_node]
            }
        end,
        Nodes
    ).