module Views.Alert exposing (error)

import Html exposing (..)
import Html.Attributes exposing (..)
import Http


error : Http.Error -> Html msg
error error =
    let
        str =
            case error of
                Http.BadStatus response ->
                    response.body

                _ ->
                    toString error
    in
        div [ class "alert alert-danger alert-dismissable" ]
            [ span [ class "glyphicon glyphicon-exclamation-sign" ] []
            , text (" Error: " ++ str)
            ]
