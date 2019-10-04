module Page.Timetables.Timetable
    exposing
        ( Model
        , Msg
        , initialModel
        , update
        , view
        , subscriptions
        )

import DefaultDict exposing (DefaultDict)
import Html exposing (..)
import Html.Attributes exposing (..)
import Html.Events exposing (..)
import Keyboard
import Mouse exposing (Position)


-- MODEL


type alias Model =
    { events : DefaultDict Int (List Event)
    , eventPreview : Maybe EventPreview
    }


type alias Event =
    -- TODO Create Data.Event with all fields.
    { duration : Duration }


type alias Duration =
    { start : Int
    , end : Int
    }


type alias EventPreview =
    { day : Int
    , start : Int
    , current : Int
    , show : Bool
    }


type Msg
    = CreateEventPreview Int Int
    | ExtendEventPreview Int Int
    | CompleteEventPreview
    | HideEventPreview
    | RemoveEventPreview Position
    | KeyDown Int


initialModel : Model
initialModel =
    { events = DefaultDict.empty []
    , eventPreview = Nothing
    }


dayNames : List String
dayNames =
    [ "Mon", "Tue", "Wed", "Thu", "Fri" ]


days : List Int
days =
    List.range 0 (List.length dayNames - 1)


periods : List ( Int, String )
periods =
    let
        firstHour =
            7

        str x =
            toString (x + firstHour)

        toText x =
            str x ++ ":00-" ++ str x ++ ":50"
    in
        List.map (\x -> ( x, toText x )) (List.range 0 12)



-- UPDATE


update : Msg -> Model -> ( Model, Cmd Msg )
update msg model =
    case msg of
        CreateEventPreview day start ->
            let
                newPreview =
                    Just { day = day, start = start, current = start, show = True }
            in
                ( { model | eventPreview = newPreview }, Cmd.none )

        ExtendEventPreview day current ->
            let
                newPreview =
                    model.eventPreview
                        |> Maybe.map (extendEventPreview day current)
                        |> Maybe.map (\preview -> { preview | show = True })
            in
                ( { model | eventPreview = newPreview }, Cmd.none )

        CompleteEventPreview ->
            ( { model | eventPreview = Nothing, events = getAllEvents model }
            , Cmd.none
            )

        HideEventPreview ->
            let
                newPreview =
                    model.eventPreview
                        |> Maybe.map (\preview -> { preview | show = False })
            in
                ( { model | eventPreview = newPreview }, Cmd.none )

        RemoveEventPreview _ ->
            ( { model | eventPreview = Nothing }, Cmd.none )

        KeyDown keyCode ->
            case keyCode of
                27 ->
                    ( { model | eventPreview = Nothing }, Cmd.none )

                _ ->
                    ( model, Cmd.none )


extendEventPreview : Int -> Int -> EventPreview -> EventPreview
extendEventPreview day period preview =
    if day == preview.day then
        { preview | current = period }
    else
        preview


toDuration : EventPreview -> Duration
toDuration { start, current } =
    if current < start then
        { start = current, end = start }
    else
        { start = start, end = current }


getAllEvents : Model -> DefaultDict Int (List Event)
getAllEvents { eventPreview, events } =
    case eventPreview of
        Just preview ->
            if preview.show then
                DefaultDict.update preview.day
                    (Just << (::) (Event (toDuration preview)))
                    events
            else
                events

        Nothing ->
            events



-- SUBSCRIPTIONS


subscriptions : Model -> Sub Msg
subscriptions model =
    let
        isCursorOutsideGrid =
            model.eventPreview
                |> Maybe.map (not << .show)
                |> Maybe.withDefault False

        removeSub =
            if isCursorOutsideGrid then
                Mouse.ups RemoveEventPreview
            else
                Sub.none
    in
        Sub.batch [ removeSub, Keyboard.downs KeyDown ]



-- VIEW


view : Bool -> Model -> Html Msg
view isUserAdmin model =
    div [ class "container" ]
        [ div [ class "page-header" ] [ h2 [] [ text "Timetable" ] ]
        , div [ class "timetable" ]
            [ viewGrid isUserAdmin
            , viewEvents isUserAdmin model
            ]
        ]


viewGrid : Bool -> Html Msg
viewGrid isUserAdmin =
    let
        headings =
            List.map viewGridHeading dayNames
    in
        table [ class "timetable-grid" ]
            [ thead [] [ tr [] (th [ class "time-col" ] [] :: headings) ]
            , tbody [] (List.map (viewGridRow isUserAdmin days) periods)
            ]


viewGridHeading : String -> Html msg
viewGridHeading day =
    th [ class "text-center" ] [ text day ]


viewGridRow : Bool -> List Int -> ( Int, String ) -> Html Msg
viewGridRow isUserAdmin days ( periodId, periodText ) =
    let
        cells =
            List.map (viewGridCell isUserAdmin periodId) days
    in
        tr [] (td [ class "time-col text-right" ] [ text periodText ] :: cells)


viewGridCell : Bool -> Int -> Int -> Html Msg
viewGridCell isUserAdmin periodId day =
    let
        listeners =
            if isUserAdmin then
                [ onMouseDown (CreateEventPreview day periodId)
                , onMouseOver (ExtendEventPreview day periodId)
                , onMouseUp CompleteEventPreview
                , onMouseLeave HideEventPreview
                ]
            else
                []
    in
        td listeners []


viewEvents : Bool -> Model -> Html Msg
viewEvents isUserAdmin model =
    let
        previewExists =
            model.eventPreview /= Nothing

        eventsByDay day =
            DefaultDict.get day (getAllEvents model)

        events =
            List.map (viewEventCol isUserAdmin previewExists << eventsByDay) days
    in
        table [ class "timetable-skeleton" ]
            [ tbody [] [ tr [] (td [ class "time-col" ] [] :: events) ] ]


viewEventCol : Bool -> Bool -> List Event -> Html Msg
viewEventCol isUserAdmin previewExists events =
    td []
        [ div [ class "event-container" ]
            (List.map (viewEvent isUserAdmin previewExists) events)
        ]


viewEvent : Bool -> Bool -> Event -> Html Msg
viewEvent isUserAdmin previewExists { duration } =
    let
        { start, end } =
            duration

        rowHeight =
            50

        rows =
            end - start + 1

        -- Let pointer events through to grid if we are creating a new event.
        pointerEvents =
            if previewExists then
                ( "pointer-events", "none" )
            else
                ( "pointer-events", "auto" )

        cursorStyle =
            if isUserAdmin then
                ( "cursor", "pointer" )
            else
                ( "cursor", "auto" )

        css =
            style
                [ ( "top", toString (30 + start * rowHeight + 3) ++ "px" )
                , ( "height", toString (rowHeight * rows - 5) ++ "px" )
                , cursorStyle
                , pointerEvents
                ]

        listeners =
            if previewExists then
                [ onMouseUp CompleteEventPreview ]
            else
                []
    in
        div ([ class "event", css ] ++ listeners) []
