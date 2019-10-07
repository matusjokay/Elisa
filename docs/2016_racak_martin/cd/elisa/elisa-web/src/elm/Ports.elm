port module Ports exposing (storeToken, removeToken)


port storeToken : String -> Cmd msg


port removeToken : () -> Cmd msg
