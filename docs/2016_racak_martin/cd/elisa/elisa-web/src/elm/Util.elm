module Util exposing (apiUrl, onClickPreventDefault)

import Html exposing (Attribute)
import Html.Events exposing (onWithOptions)
import Json.Decode as Decode


apiUrl : String -> String
apiUrl path =
    "http://localhost:8000" ++ path


onClickPreventDefault : msg -> Attribute msg
onClickPreventDefault msg =
    onWithOptions
        "click"
        { preventDefault = True
        , stopPropagation = False
        }
        (Decode.succeed msg)
