module Data.User exposing (User, fromToken, httpConfig, tokenDecoder)

import Http
import Json.Decode as Decode exposing (Decoder)
import Jwt
import RemoteData.Http


type alias User =
    { token : String
    , username : String
    }


fromToken : String -> Maybe User
fromToken token =
    token
        |> getUsername
        |> Maybe.map (User token)


getUsername : String -> Maybe String
getUsername =
    Result.toMaybe << Jwt.decodeToken usernameDecoder


usernameDecoder : Decoder String
usernameDecoder =
    Decode.field "username" Decode.string


tokenDecoder : Decoder String
tokenDecoder =
    Decode.field "token" Decode.string


httpConfig : Maybe User -> RemoteData.Http.Config
httpConfig maybeUser =
    case maybeUser of
        Just user ->
            { headers = [ Http.header "Authorization" ("JWT " ++ user.token) ]
            , withCredentials = True
            , timeout = Nothing
            }

        Nothing ->
            RemoteData.Http.defaultConfig
