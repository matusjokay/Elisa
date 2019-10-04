module Route exposing (Route(..), route, parseLocation, navigateTo)

import Html exposing (Attribute, Html)
import Html.Attributes exposing (..)
import Navigation exposing (Location)
import UrlParser as Url exposing (s, top, int, (</>))
import Util exposing (onClickPreventDefault)


type Route
    = Home
    | Timetables
    | Timetable Int
    | Courses
    | Course Int
    | NotFound


route : Url.Parser (Route -> a) a
route =
    Url.oneOf
        [ Url.map Home top
        , Url.map Timetables (s "timetables")
        , Url.map Timetable (s "timetables" </> int)
        , Url.map Courses (s "courses")
        , Url.map Course (s "courses" </> int)
        ]


reverseRoute : Route -> String
reverseRoute route =
    case route of
        Home ->
            "/"

        NotFound ->
            "/"

        Timetables ->
            "/timetables"

        Timetable id ->
            "/timetables/" ++ toString id

        Courses ->
            "/courses"

        Course id ->
            "/courses" ++ toString id


parseLocation : Location -> Route
parseLocation location =
    location
        |> Url.parsePath route
        |> Maybe.withDefault NotFound


{-| We need this to use hash-less URLs for navigation. We want to avoid using #
for SPA routing to make URLs which contain query params (i.e. pointing to a
timetable with applied filters) correct and look nicer.

See this post for more info:

<https://medium.com/elm-shorts/choosing-the-right-elm-spa-architecture-d6e8275f6899>

-}
navigateTo : (String -> msg) -> Route -> List (Attribute msg)
navigateTo navigateMsg route =
    let
        url =
            reverseRoute route
    in
        [ href url, onClickPreventDefault (navigateMsg url) ]
