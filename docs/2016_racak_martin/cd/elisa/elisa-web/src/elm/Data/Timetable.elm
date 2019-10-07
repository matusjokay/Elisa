module Data.Timetable exposing (Timetable, decoder, listDecoder)

import Date exposing (Date)
import Json.Decode as Decode exposing (Decoder)
import Json.Decode.Extra
import Json.Decode.Pipeline exposing (decode, required)


type alias Timetable =
    { id : Int
    , name : String
    , dateStart : Date
    , dateEnd : Date
    }


decoder : Decoder Timetable
decoder =
    decode Timetable
        |> required "id" Decode.int
        |> required "name" Decode.string
        |> required "date_start" Json.Decode.Extra.date
        |> required "date_end" Json.Decode.Extra.date


listDecoder : Decoder (List Timetable)
listDecoder =
    Decode.at [ "results" ] (Decode.list decoder)
