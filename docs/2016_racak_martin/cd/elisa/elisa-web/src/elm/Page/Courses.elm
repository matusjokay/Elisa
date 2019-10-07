module Page.Courses
    exposing
        ( Model
        , Msg
        , initialModel
        , update
        , getCourses
        , view
        )

import Data.Course as Course exposing (Course)
import Html exposing (..)
import Html.Attributes exposing (..)
import RemoteData exposing (RemoteData(..), WebData)
import RemoteData.Http
import Util exposing (apiUrl)
import Views.Alert as Alert


type alias Model =
    { courses : WebData (List Course) }


initialModel : Model
initialModel =
    { courses = Loading }


type Msg
    = HandleCourses (WebData (List Course))


update : Msg -> Model -> ( Model, Cmd Msg )
update msg model =
    case msg of
        HandleCourses webData ->
            ( { model | courses = webData }, Cmd.none )


getCourses : Cmd Msg
getCourses =
    RemoteData.Http.get (apiUrl "/courses/") HandleCourses Course.listDecoder


view : Model -> Html msg
view model =
    let
        content =
            case model.courses of
                Loading ->
                    [ text "Loading..." ]

                Failure error ->
                    [ Alert.error error ]

                Success courses ->
                    [ h2 [] [ text "Courses" ]
                    , table [ class "table" ]
                        [ thead []
                            [ tr []
                                [ th [] [ text "ID" ]
                                , th [] [ text "Name" ]
                                , th [] [ text "Code" ]
                                , th [] [ text "Department" ]
                                ]
                            ]
                        , tbody [] (List.map viewCourseRow courses)
                        ]
                    ]

                _ ->
                    [ text "" ]
    in
        div [ class "container" ] content


viewCourseRow : Course -> Html msg
viewCourseRow course =
    tr []
        [ td [] [ text (toString course.id) ]
        , td [] [ text course.name ]
        , td [] [ text course.code ]
        , td [] [ text (toString course.department) ]
        ]
