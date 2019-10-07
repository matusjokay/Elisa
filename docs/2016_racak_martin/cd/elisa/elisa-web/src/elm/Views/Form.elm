module Views.Form exposing (textGroup, dateGroup, passwordGroup)

import Form exposing (FieldState)
import Form.Error exposing (Error, ErrorValue)
import Form.Field as Field
import Form.Input as Input
import Html exposing (..)
import Html.Attributes exposing (..)


type alias GroupBuilder a =
    Html Form.Msg -> FieldState () a -> Html Form.Msg


formGroup :
    Html Form.Msg
    -> Maybe (ErrorValue ())
    -> List (Html Form.Msg)
    -> Html Form.Msg
formGroup label_ maybeError inputs =
    div
        [ class ("form-group " ++ errorClass maybeError) ]
        [ label [ class "col-sm-2 control-label" ] [ label_ ]
        , div [ class "col-sm-10" ] (inputs ++ [ errorMessage maybeError ])
        ]


textGroup : GroupBuilder String
textGroup label_ state =
    formGroup label_
        state.liveError
        [ Input.textInput state
            [ class "form-control"
            , value (Maybe.withDefault "" state.value)
            ]
        ]


dateGroup : GroupBuilder String
dateGroup label_ state =
    formGroup label_
        state.liveError
        [ Input.baseInput "date"
            Field.String
            Form.Text
            state
            [ class "form-control"
            , value (Maybe.withDefault "" state.value)
            , placeholder "yyyy-mm-dd"
            ]
        ]


passwordGroup : GroupBuilder String
passwordGroup label_ state =
    formGroup label_
        state.liveError
        [ Input.textInput state
            [ class "form-control"
            , type_ "password"
            , value (Maybe.withDefault "" state.value)
            ]
        ]


textAreaGroup : GroupBuilder String
textAreaGroup label_ state =
    formGroup label_
        state.liveError
        [ Input.textArea state
            [ class "form-control"
            , value (Maybe.withDefault "" state.value)
            ]
        ]


checkboxGroup : GroupBuilder Bool
checkboxGroup label_ state =
    formGroup (text "")
        state.liveError
        [ div
            [ class "checkbox" ]
            [ label []
                [ Input.checkboxInput state []
                , label_
                ]
            ]
        ]


selectGroup : List ( String, String ) -> GroupBuilder String
selectGroup options label_ state =
    formGroup label_
        state.liveError
        [ Input.selectInput options state [ class "form-control" ] ]


radioGroup : List ( String, String ) -> GroupBuilder String
radioGroup options label_ state =
    let
        item ( v, l ) =
            label
                [ class "radio-inline" ]
                [ Input.radioInput v state []
                , text l
                ]
    in
        formGroup label_
            state.liveError
            (List.map item options)


errorClass : Maybe error -> String
errorClass maybeError =
    Maybe.map (\_ -> "has-error") maybeError |> Maybe.withDefault ""


errorMessage : Maybe (ErrorValue ()) -> Html Form.Msg
errorMessage maybeError =
    case maybeError of
        Just error ->
            span
                [ class "help-block" ]
                [ text (toString error) ]

        Nothing ->
            text ""
