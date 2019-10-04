module Page.Timetables
    exposing
        ( Model
        , Msg
        , initialModel
        , view
        , update
        , getTimetables
        )

import Data.Timetable as Timetable exposing (Timetable)
import Data.User as User exposing (User)
import Date.Extra.Format exposing (isoDateString)
import Dialog
import Form exposing (Form)
import Form.Field as Field exposing (Field)
import Form.Validate as Validate exposing (..)
import Html exposing (..)
import Html.Attributes exposing (..)
import Html.Events exposing (..)
import Http
import Json.Encode as Encode
import Navigation
import RemoteData exposing (RemoteData(..), WebData)
import RemoteData.Http
import Route
import Util exposing (apiUrl)
import Views.Alert as Alert
import Views.Form exposing (textGroup, dateGroup)


type alias Model =
    { timetables : WebData (List Timetable)
    , currentTimetable : Maybe Timetable
    , dialogError : Maybe Http.Error
    , formType : Maybe FormType
    , form : Form () Timetable
    }


type FormType
    = New
    | Edit


type Msg
    = HandleTimetables (WebData (List Timetable))
    | HandleCreateTimetable (WebData Timetable)
    | HandleUpdateTimetable (WebData Timetable)
    | HandleDeleteTimetable (WebData String)
    | NewTimetable
    | EditTimetable Int
    | DeleteTimetable Int
    | CloseDialog
    | FormMsg Form.Msg
    | NewUrl String


initialModel : Model
initialModel =
    { timetables = Loading
    , currentTimetable = Nothing
    , dialogError = Nothing
    , formType = Nothing
    , form = Form.initial [] validate
    }


initialFields : Timetable -> List ( String, Field )
initialFields timetable =
    [ ( "id", Field.string (toString timetable.id) )
    , ( "name", Field.string timetable.name )
    , ( "dateStart", Field.string (isoDateString timetable.dateStart) )
    , ( "dateEnd", Field.string (isoDateString timetable.dateEnd) )
    ]


validate : Validation () Timetable
validate =
    map4 Timetable
        (field "id" int |> Validate.defaultValue 0)
        (field "name" string)
        (field "dateStart" date)
        (field "dateEnd" date)


update : Maybe User -> Msg -> Model -> ( Model, Cmd Msg )
update maybeUser msg model =
    case msg of
        HandleTimetables webData ->
            ( { model | timetables = webData }, Cmd.none )

        HandleCreateTimetable webData ->
            case webData of
                Success _ ->
                    ( { model | dialogError = Nothing, formType = Nothing }
                    , getTimetables
                    )

                Failure error ->
                    ( { model | dialogError = Just error }, Cmd.none )

                _ ->
                    ( model, Cmd.none )

        HandleUpdateTimetable webData ->
            case webData of
                Success _ ->
                    ( { model | dialogError = Nothing, formType = Nothing }
                    , getTimetables
                    )

                Failure error ->
                    ( { model | dialogError = Just error }, Cmd.none )

                _ ->
                    ( model, Cmd.none )

        HandleDeleteTimetable webData ->
            case webData of
                Success _ ->
                    ( model, getTimetables )

                Failure error ->
                    ( { model | timetables = Failure error }, Cmd.none )

                _ ->
                    ( model, Cmd.none )

        NewTimetable ->
            ( { model
                | formType = Just New
                , form = Form.initial [] validate
              }
            , Cmd.none
            )

        EditTimetable id ->
            let
                fields =
                    model.timetables
                        |> RemoteData.toMaybe
                        |> Maybe.map (List.filter (\x -> x.id == id))
                        |> Maybe.andThen List.head
                        |> Maybe.map initialFields
                        |> Maybe.withDefault []
            in
                ( { model
                    | formType = Just Edit
                    , form = Form.initial fields validate
                  }
                , Cmd.none
                )

        DeleteTimetable id ->
            ( model, deleteTimetable maybeUser id )

        CloseDialog ->
            ( { model | dialogError = Nothing, formType = Nothing }, Cmd.none )

        FormMsg formMsg ->
            case ( formMsg, Form.getOutput model.form ) of
                ( Form.Submit, Just timetable ) ->
                    case model.formType of
                        Just New ->
                            ( model, createTimetable maybeUser timetable )

                        Just Edit ->
                            ( model, updateTimetable maybeUser timetable )

                        Nothing ->
                            ( model, Cmd.none )

                _ ->
                    ( { model | form = Form.update validate formMsg model.form }
                    , Cmd.none
                    )

        NewUrl url ->
            ( model, Navigation.newUrl url )


encodeTimetable : Timetable -> Encode.Value
encodeTimetable timetable =
    Encode.object
        [ ( "name", Encode.string timetable.name )
        , ( "date_start", Encode.string (isoDateString timetable.dateStart) )
        , ( "date_end", Encode.string (isoDateString timetable.dateEnd) )
        ]


getTimetables : Cmd Msg
getTimetables =
    RemoteData.Http.get
        (apiUrl "/timetables/")
        HandleTimetables
        Timetable.listDecoder


createTimetable : Maybe User -> Timetable -> Cmd Msg
createTimetable maybeUser timetable =
    RemoteData.Http.postWithConfig
        (User.httpConfig maybeUser)
        (apiUrl "/timetables/")
        HandleCreateTimetable
        Timetable.decoder
        (encodeTimetable timetable)


updateTimetable : Maybe User -> Timetable -> Cmd Msg
updateTimetable maybeUser timetable =
    RemoteData.Http.putWithConfig
        (User.httpConfig maybeUser)
        (apiUrl ("/timetables/" ++ toString timetable.id ++ "/"))
        HandleUpdateTimetable
        Timetable.decoder
        (encodeTimetable timetable)


deleteTimetable : Maybe User -> Int -> Cmd Msg
deleteTimetable maybeUser id =
    RemoteData.Http.deleteWithConfig
        (User.httpConfig maybeUser)
        (apiUrl ("/timetables/" ++ toString id ++ "/"))
        HandleDeleteTimetable
        Encode.null


view : Bool -> Model -> Html Msg
view isUserAdmin model =
    let
        actions =
            if isUserAdmin then
                [ div [ class "btn-toolbar pull-right" ]
                    [ button [ class "btn btn-default", onClick NewTimetable ]
                        [ text "New" ]
                    ]
                ]
            else
                []
    in
        case model.timetables of
            NotAsked ->
                div [ class "container" ] [ text "Initializing..." ]

            Loading ->
                div [ class "container" ] [ text "Loading..." ]

            Failure error ->
                div [ class "container " ] [ Alert.error error ]

            Success timetables ->
                div [ class "container" ]
                    [ div [ class "page-header" ]
                        (actions ++ [ h2 [] [ text "Timetables " ] ])
                    , table [ class "table" ]
                        [ thead []
                            [ tr []
                                [ th [] [ text "ID" ]
                                , th [] [ text "Name" ]
                                , th [] [ text "Starts" ]
                                , th [ colspan 2 ] [ text "Ends" ]
                                ]
                            ]
                        , tbody []
                            (List.map (viewTimetableRow isUserAdmin) timetables)
                        ]
                    , model.formType
                        |> Maybe.map (dialogConfig model.form model.dialogError)
                        |> Dialog.view
                    ]


viewTimetableRow : Bool -> Timetable -> Html Msg
viewTimetableRow isUserAdmin timetable =
    let
        actions =
            if isUserAdmin then
                [ div [ class "btn-group" ]
                    [ button
                        [ class "btn btn-default btn-xs"
                        , title "Edit"
                        , onClick (EditTimetable timetable.id)
                        ]
                        [ span [ class "glyphicon glyphicon-pencil" ] [] ]
                    , button
                        [ class "btn btn-danger btn-xs"
                        , title "Delete"
                        , onClick (DeleteTimetable timetable.id)
                        ]
                        [ span [ class "glyphicon glyphicon-trash" ] [] ]
                    ]
                ]
            else
                []
    in
        tr []
            [ td [] [ text (toString timetable.id) ]
            , td []
                [ a (Route.navigateTo NewUrl (Route.Timetable timetable.id))
                    [ text timetable.name ]
                ]
            , td [] [ text (isoDateString timetable.dateStart) ]
            , td [] [ text (isoDateString timetable.dateEnd) ]
            , td [] actions
            ]


viewForm : Form () Timetable -> Html Form.Msg
viewForm form =
    div [ class "form-horizontal" ]
        [ textGroup (text "Name") (Form.getFieldAsString "name" form)
        , dateGroup (text "Starts") (Form.getFieldAsString "dateStart" form)
        , dateGroup (text "Ends") (Form.getFieldAsString "dateEnd" form)
        ]


dialogConfig :
    Form () Timetable
    -> Maybe Http.Error
    -> FormType
    -> Dialog.Config Msg
dialogConfig form responseError formType =
    let
        dialogTitle =
            case formType of
                New ->
                    "New timetable"

                Edit ->
                    "Edit timetable"

        viewError =
            responseError
                |> Maybe.map Alert.error
                |> Maybe.withDefault (text "")
    in
        { closeMessage = Just CloseDialog
        , containerClass = Nothing
        , header = Just (h2 [ class "modal-title" ] [ text dialogTitle ])
        , body =
            Just (div [] [ viewError, Html.map FormMsg (viewForm form) ])
        , footer =
            Just <|
                div []
                    [ button
                        [ class "btn btn-default", onClick CloseDialog ]
                        [ text "Cancel" ]
                    , button
                        [ class "btn btn-primary"
                        , onClick (FormMsg Form.Submit)
                        ]
                        [ text "Save" ]
                    ]
        }
