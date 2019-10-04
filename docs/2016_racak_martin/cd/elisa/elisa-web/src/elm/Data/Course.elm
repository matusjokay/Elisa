module Data.Course exposing (Course, decoder, listDecoder)

import Json.Decode as Decode exposing (Decoder)
import Json.Decode.Pipeline exposing (decode, required)


type alias Course =
    { id : Int
    , name : String
    , code : String
    , department : Int
    }


decoder : Decoder Course
decoder =
    decode Course
        |> required "id" Decode.int
        |> required "name" Decode.string
        |> required "code" Decode.string
        |> required "department" Decode.int


listDecoder : Decoder (List Course)
listDecoder =
    Decode.at [ "results" ] (Decode.list decoder)
