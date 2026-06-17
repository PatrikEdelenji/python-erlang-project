-module(network_sup).

-behaviour(supervisor).

-export([start_link/0]).
-export([init/1]).

start_link() ->
    supervisor:start_link({local, ?MODULE}, ?MODULE, []).

init([]) ->
    Children = [
        #{
            id => erlang_node_001,
            start => {network_node, start_link, ["erlang_node_001", stable]},
            restart => permanent,
            shutdown => 5000,
            type => worker,
            modules => [network_node]
        },
        #{
            id => erlang_node_002,
            start => {network_node, start_link, ["erlang_node_002", unstable]},
            restart => permanent,
            shutdown => 5000,
            type => worker,
            modules => [network_node]
        },
        #{
            id => erlang_node_003,
            start => {network_node, start_link, ["erlang_node_003", critical]},
            restart => permanent,
            shutdown => 5000,
            type => worker,
            modules => [network_node]
        }
    ],

    SupFlags = #{
        strategy => one_for_one,
        intensity => 5,
        period => 10
    },

    {ok, {SupFlags, Children}}.