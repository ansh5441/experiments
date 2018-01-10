%% name of module must match file name
%% erlc  -I /lib/ejabberd/include/  mod_http_offline.erl
%% copy to /lib/ejabberd/ebin
-module(mod_http_offline).
-author("Rael Max").
 
-behaviour(gen_mod).
 
-export([start/2, stop/1, create_message/3]).
 
-include("ejabberd.hrl").
-include("jlib.hrl").
 
start(_Host, _Opt) ->
    inets:start(),
    ejabberd_hooks:add(offline_message_hook, _Host, ?MODULE, create_message, 50).  
 
stop (_Host) ->
    ejabberd_hooks:delete(offline_message_hook, _Host, ?MODULE, create_message, 50).
 
create_message(_From, _To, Packet) ->
    MessageId = xml:get_tag_attr_s(list_to_binary("id"), Packet),
    Type = xml:get_tag_attr_s(list_to_binary("type"), Packet),
    FromS = _From#jid.luser,
    ToS = _To#jid.luser,
    Body = xml:get_path_s(Packet, [{elem, list_to_binary("body")}, cdata]),

    if (Type == <<"chat">>) and (Body /= <<"">>) ->
        post_offline_message(FromS, ToS, Body, MessageId)
    end.
 
post_offline_message(From, To, Body, MessageId) ->
    Sep = "&",
    Post = [
        "from=", From, Sep,
        "to=", To, Sep,
        "body=", binary_to_list(Body), Sep,
        "message_id=", binary_to_list(MessageId), Sep,
        "access_token=123-secret-key"
    ],
    httpc:request(post, {"http://54.208.101.63/", [], "application/x-www-form-urlencoded", list_to_binary(Post)},[],[]).